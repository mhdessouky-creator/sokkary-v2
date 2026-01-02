import google.generativeai as genai
import logging
import asyncio
import json
import re
from config.config import Config

class GeminiOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.configured = False

        if Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                self.configured = True
            except Exception as e:
                self.logger.error(f"Failed to configure Gemini: {e}")
        else:
            self.logger.warning("Gemini API Key not found.")

    def _extract_json(self, text: str) -> dict:
        text = text.strip()

        # Try to find markdown block first
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            code_block = match.group(1)
            try:
                return json.loads(code_block)
            except json.JSONDecodeError:
                pass # Continue if markdown content isn't valid JSON

        # If no markdown block or parsing failed, try to find the first '{' and last '}'
        # This handles cases like "Here is the JSON: {...}"
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Finally, try raw text just in case
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    async def process_request(self, user_input: str, history: list = None) -> str:
        """
        Processes user request using Gemini.
        Acts as an orchestrator (can be expanded to delegate tasks).
        """
        if not self.configured:
            return "Gemini is not configured. Please check your .env file."

        try:
            self.logger.info("Sending request to Gemini...")
            chat = self.model.start_chat(history=history if history else [])
            response = await chat.send_message_async(user_input)
            return response.text
        except Exception as e:
            self.logger.error(f"Gemini Error: {e}")
            return f"Error processing request: {str(e)}"

    async def analyze_task(self, task_description: str) -> dict:
        """
        Analyzes a task to decide if it needs code execution or other agents.
        Returns a structured decision containing action and potentially code.
        """
        if not self.configured:
            return {"action": "error", "details": "Gemini not configured"}

        prompt = f"""
        Analyze the following user request.
        Determine if the user wants to execute Python code or just chat.

        If the user wants to execute code, you MUST generate the Python code to fulfill the request.

        Return your response in STRICT JSON format with the following keys:
        - "action": "code" or "chat"
        - "code": The Python code to execute (only if action is "code"). Do not include markdown code blocks inside this string value.
        - "response": A conversational response (if action is "chat" or to accompany the code).

        Request: {task_description}
        """
        try:
            response = await self.model.generate_content_async(prompt)
            text_response = response.text

            data = self._extract_json(text_response)

            if data:
                # Ensure the original response text is also preserved if needed, though we rely on parsed data
                data["original_response"] = text_response
                return data
            else:
                # Fallback: Check for 'CODE' word if JSON parsing failed
                self.logger.warning("Failed to parse JSON from analysis response. Falling back to text check.")
                decision = text_response.strip().upper()
                return {"action": "code" if "CODE" in decision else "chat", "original_response": text_response}

        except Exception as e:
            self.logger.error(f"Task Analysis Error: {e}")
            return {"action": "chat", "error": str(e)}
