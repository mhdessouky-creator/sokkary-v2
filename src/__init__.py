"""
Sokkary V2 - AI Multi-Agent System
"""

__version__ = "0.1.0"
__author__ = "mhdessouky-creator"
__description__ = "AI Multi-Agent System with LangGraph, MCP, Tools, and Skills"

from src.agents import (
    BaseAgent,
    OrchestratorAgent,
    PlannerAgent,
    ExecutorAgent,
    ValidatorAgent,
)
from src.config import Settings

__all__ = [
    "BaseAgent",
    "OrchestratorAgent",
    "PlannerAgent",
    "ExecutorAgent",
    "ValidatorAgent",
    "Settings",
    "__version__",
]
