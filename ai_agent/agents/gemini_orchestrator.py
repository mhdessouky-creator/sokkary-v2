import google.generativeai as genai
import logging
import asyncio
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
        Returns a structured decision (simulated here as we expect JSON or text analysis).
        """
        if not self.configured:
            return {"action": "error", "details": "Gemini not configured"}

        prompt = f"""
        Analyze the following user request and decide if it requires code execution.
        Request: {task_description}

        Respond with 'CODE' if it needs code execution, or 'CHAT' if it's a conversational query.
        """
        try:
            response = await self.model.generate_content_async(prompt)
            decision = response.text.strip().upper()
            return {"action": "code" if "CODE" in decision else "chat", "original_response": response.text}
        except Exception as e:
            self.logger.error(f"Task Analysis Error: {e}")
            return {"action": "chat", "error": str(e)}
