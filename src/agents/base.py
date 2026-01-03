from abc import ABC, abstractmethod
from typing import List, Any, Optional
from src.core.state import SharedState
import logging

# Configure a basic logger for now, can be improved later
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, model_client: Any = None, tools: Optional[List[Any]] = None):
        self.name = name
        self.model_client = model_client
        self.tools = tools or []

    @abstractmethod
    async def process(self, state: SharedState) -> SharedState:
        """
        Process the current state and return the updated state.
        This method must be implemented by concrete agent classes.
        """
        pass

    def log_thought(self, message: str):
        """Standard logging mechanism to trace agent thoughts."""
        logger.info(f"[{self.name}] {message}")
