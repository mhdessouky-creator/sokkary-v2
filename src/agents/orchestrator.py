"""
Orchestrator Agent - Analyzes tasks and routes to appropriate agents
"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentState
from src.config.prompts import AgentPrompts
from src.utils.logger import get_logger
from src.utils.helpers import validate_dict_structure

logger = get_logger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent

    Responsibilities:
    - Analyze incoming user requests
    - Determine task complexity
    - Identify required tools and skills
    - Make routing decisions
    """

    def __init__(self, **kwargs):
        super().__init__(agent_type="orchestrator", **kwargs)

    def execute(self, state: AgentState) -> AgentState:
        """
        Analyze the user request and make routing decisions

        Args:
            state: Current agent state

        Returns:
            Updated state with orchestrator output
        """
        logger.info(f"Orchestrator analyzing: {state.user_input[:100]}...")

        # Update state
        state.add_to_history("orchestrator")

        try:
            # Create context and generate prompt
            context = self._create_context(state)
            user_prompt = AgentPrompts.get_user_prompt("orchestrator", context)

            # Call model
            response = self._call_model(user_prompt)
            logger.debug(f"Orchestrator raw response: {response}")

            # Parse response
            output = self._parse_json_response(response)

            # Validate output
            if not self.validate_output(output):
                logger.warning("Orchestrator output validation failed, using defaults")
                output = self._create_default_output(state.user_input)

            # Update state
            state.orchestrator_output = output

            logger.info(
                f"Orchestrator decision: {output.get('routing_decision')} "
                f"(complexity: {output.get('complexity')})"
            )

            return state

        except Exception as e:
            error_msg = f"Orchestrator execution failed: {str(e)}"
            logger.error(error_msg)
            state.add_error(error_msg)

            # Use default output on failure
            state.orchestrator_output = self._create_default_output(state.user_input)
            return state

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate orchestrator output structure

        Args:
            output: Output dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_keys = [
            "complexity",
            "requires_planning",
            "routing_decision",
        ]

        is_valid = validate_dict_structure(output, required_keys)

        if is_valid:
            # Validate enum values
            valid_complexity = output["complexity"] in ["simple", "medium", "complex"]
            valid_routing = output["routing_decision"] in ["direct_execution", "full_pipeline"]
            is_valid = valid_complexity and valid_routing

        return is_valid

    def _create_default_output(self, user_input: str) -> Dict[str, Any]:
        """
        Create default output when analysis fails

        Args:
            user_input: Original user input

        Returns:
            Default orchestrator output
        """
        return {
            "complexity": "medium",
            "requires_planning": True,
            "required_tools": [],
            "required_skills": [],
            "routing_decision": "full_pipeline",
            "reasoning": "Using default full pipeline due to analysis failure"
        }
