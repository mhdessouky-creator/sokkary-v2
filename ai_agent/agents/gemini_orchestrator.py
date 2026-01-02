import google.generativeai as genai
import logging
import asyncio
import json
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
        Returns a structured decision using JSON parsing.
        """
        if not self.configured:
            return {"action": "error", "details": "Gemini not configured"}

        prompt = f"""
        You are an AI assistant orchestrator. Your job is to analyze the user's request and determine the best course of action.

        Available Actions:
        - CHAT: For general conversation, questions, or explanations that do not require running code.
        - CODE: If the user wants to calculate something, manipulate files, analyze data, or run a specific algorithm.
        - TOOL: If the user specifically asks for FPL (Fantasy Premier League) news or football updates.

        User Request: {task_description}

        Respond with a pure JSON object (no markdown formatting) with the following schema:
        {{
          "action": "CHAT" | "CODE" | "TOOL",
          "tool_name": "fpl_news" (only if action is TOOL),
          "reasoning": "Brief explanation of why this action was chosen",
          "suggested_description": "Refined description of the code task if action is CODE (optional)"
        }}
        """
        try:
            response = await self.model.generate_content_async(prompt)
            text_response = response.text.strip()

            # clean up markdown if present
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            elif text_response.startswith("```"):
                text_response = text_response[3:]

            if text_response.endswith("```"):
                text_response = text_response[:-3]

            try:
                data = json.loads(text_response.strip())
                return {
                    "action": data.get("action", "CHAT").lower(),
                    "tool_name": data.get("tool_name", ""),
                    "reasoning": data.get("reasoning", ""),
                    "suggested_description": data.get("suggested_description", task_description),
                    "original_response": text_response
                }
            except json.JSONDecodeError:
                self.logger.warning(f"Failed to parse JSON from Gemini: {text_response}")
                # Fallback to simple keyword detection
                upper_response = text_response.upper()
                if "TOOL" in upper_response or "FPL" in upper_response:
                    return {"action": "tool", "tool_name": "fpl_news", "original_response": text_response}
                if "CODE" in upper_response:
                     return {"action": "code", "original_response": text_response}
                return {"action": "chat", "original_response": text_response}

        except Exception as e:
            self.logger.error(f"Task Analysis Error: {e}")
            return {"action": "chat", "error": str(e)}
