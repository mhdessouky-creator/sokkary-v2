import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("API_KEY_GEMINI")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SANDBOX_DIR = os.path.join(BASE_DIR, os.getenv("SANDBOX_DIR", "sandbox"))
    EXPORT_DIR = os.path.join(BASE_DIR, os.getenv("EXPORT_DIR", "exports"))
    LOGS_DIR = os.path.join(BASE_DIR, "logs")

    @staticmethod
    def setup_logging():
        if not os.path.exists(Config.LOGS_DIR):
            os.makedirs(Config.LOGS_DIR)

        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(Config.LOGS_DIR, "system.log")),
                logging.StreamHandler()
            ]
        )

    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY:
            logging.warning("API_KEY_GEMINI is not set in .env file.")
