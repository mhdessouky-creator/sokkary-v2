"""
Base Agent class for Sokkary V2
Abstract base for all agent implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import json
from src.config.settings import settings
from src.config.prompts import AgentPrompts
from src.utils.logger import get_logger
from src.utils.helpers import measure_time, safe_get

logger = get_logger(__name__)


class AgentState(BaseModel):
    """
    State model for agent execution
    """
    user_input: str = Field(..., description="Original user input")
    orchestrator_output: Optional[Dict[str, Any]] = Field(None, description="Output from orchestrator")
    planner_output: Optional[Dict[str, Any]] = Field(None, description="Output from planner")
    executor_output: Optional[Dict[str, Any]] = Field(None, description="Output from executor")
    validator_output: Optional[Dict[str, Any]] = Field(None, description="Output from validator")

    # Metadata
    current_agent: Optional[str] = Field(None, description="Currently executing agent")
    execution_history: List[str] = Field(default_factory=list, description="Agent execution history")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")

    # Tools and skills
    available_tools: List[str] = Field(default_factory=list, description="Available tools")
    available_skills: List[str] = Field(default_factory=list, description="Available skills")

    # Final output
    final_output: Optional[str] = Field(None, description="Final output to user")

    model_config = {"arbitrary_types_allowed": True}

    def add_to_history(self, agent_name: str) -> None:
        """Add agent to execution history"""
        self.execution_history.append(agent_name)
        self.current_agent = agent_name

    def add_error(self, error: str) -> None:
        """Add error to error list"""
        self.errors.append(error)
        logger.error(f"Agent error: {error}")


class BaseAgent(ABC):
    """
    Abstract base class for all agents

    All agents must implement:
    - execute(): Main execution logic
    - validate_output(): Output validation
    """

    def __init__(
        self,
        agent_type: str,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize base agent

        Args:
            agent_type: Type of agent (orchestrator, planner, executor, validator)
            model_name: Model to use (defaults to settings.default_model)
            temperature: Sampling temperature (defaults to settings.temperature)
            max_tokens: Max tokens (defaults to settings.max_tokens)
        """
        self.agent_type = agent_type
        self.model_name = model_name or settings.default_model
        self.temperature = temperature or settings.temperature
        self.max_tokens = max_tokens or settings.max_tokens

        # Validate model availability
        if not settings.validate_model(self.model_name):
            logger.warning(
                f"Model {self.model_name} not available. "
                f"Available models: {settings.available_models}"
            )
            self.model_name = "kimi"  # Fallback to Kimi

        # Get system prompt
        self.system_prompt = AgentPrompts.get_prompt(agent_type)

        # Initialize model client
        self.model_config = settings.get_model_config(self.model_name)
        self.client = self._initialize_client()

        logger.info(
            f"Initialized {agent_type} agent with model: {self.model_name}"
        )

    def _initialize_client(self):
        """
        Initialize the appropriate model client based on model_name

        Returns:
            Model client instance
        """
        if self.model_name == "kimi":
            from openai import OpenAI
            return OpenAI(
                api_key=self.model_config["api_key"],
                base_url=self.model_config["api_url"],
            )
        elif self.model_name == "claude":
            from anthropic import Anthropic
            return Anthropic(api_key=self.model_config["api_key"])
        elif self.model_name == "groq":
            from openai import OpenAI
            return OpenAI(
                api_key=self.model_config["api_key"],
                base_url="https://api.groq.com/openai/v1",
            )
        elif self.model_name == "openai":
            from openai import OpenAI
            return OpenAI(api_key=self.model_config["api_key"])
        else:
            raise ValueError(f"Unknown model: {self.model_name}")

    def _call_model(self, user_prompt: str) -> str:
        """
        Call the model with system and user prompts

        Args:
            user_prompt: User prompt to send

        Returns:
            Model response as string
        """
        try:
            if self.model_name == "claude":
                # Anthropic Claude API
                response = self.client.messages.create(
                    model=self.model_config["model"],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.content[0].text
            else:
                # OpenAI-compatible API (Kimi, Groq, OpenAI)
                response = self.client.chat.completions.create(
                    model=self.model_config["model"],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling {self.model_name}: {e}")
            raise

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from model

        Args:
            response: Raw response string

        Returns:
            Parsed dictionary
        """
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            # Return a default error structure
            return {
                "error": "Failed to parse response",
                "raw_response": response
            }

    @abstractmethod
    @measure_time
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute the agent's main logic

        Args:
            state: Current agent state

        Returns:
            Updated agent state
        """
        pass

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate the agent's output

        Args:
            output: Output to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def _create_context(self, state: AgentState) -> Dict[str, Any]:
        """
        Create context dictionary for prompt generation

        Args:
            state: Current agent state

        Returns:
            Context dictionary
        """
        return {
            "user_input": state.user_input,
            "orchestrator_output": state.orchestrator_output,
            "planner_output": state.planner_output,
            "executor_output": state.executor_output,
            "available_tools": state.available_tools,
            "available_skills": state.available_skills,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"
