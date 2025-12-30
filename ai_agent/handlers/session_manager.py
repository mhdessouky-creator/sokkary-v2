import json
import os
import logging
from datetime import datetime

class SessionManager:
    def __init__(self, session_file="session_history.json"):
        self.logger = logging.getLogger(__name__)
        self.session_file = session_file
        self.history = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r") as f:
                    self.history = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load session history: {e}")
                self.history = []

    def save_history(self):
        try:
            with open(self.session_file, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save session history: {e}")

    def add_interaction(self, user_input, agent_response, agent_name="unknown"):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "response": agent_response,
            "agent": agent_name
        }
        self.history.append(entry)
        self.save_history()

    def get_context_for_gemini(self):
        """
        Formats history for Gemini API (user/model roles).
        """
        gemini_history = []
        for entry in self.history:
            gemini_history.append({"role": "user", "parts": [entry["user"]]})
            gemini_history.append({"role": "model", "parts": [entry["response"]]})
        return gemini_history

    def clear_history(self):
        self.history = []
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
