"""
Planner Agent - Creates detailed execution plans
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent, AgentState
from src.config.prompts import AgentPrompts
from src.utils.logger import get_logger
from src.utils.helpers import validate_dict_structure, safe_get

logger = get_logger(__name__)


class PlannerAgent(BaseAgent):
    """
    Planner Agent

    Responsibilities:
    - Receive task analysis from Orchestrator
    - Create detailed, step-by-step execution plan
    - Define success criteria
    - Identify potential risks and mitigations
    """

    def __init__(self, **kwargs):
        super().__init__(agent_type="planner", **kwargs)

    def execute(self, state: AgentState) -> AgentState:
        """
        Create a detailed execution plan

        Args:
            state: Current agent state with orchestrator output

        Returns:
            Updated state with planner output
        """
        logger.info("Planner creating execution plan...")

        # Update state
        state.add_to_history("planner")

        try:
            # Create context and generate prompt
            context = self._create_context(state)
            user_prompt = AgentPrompts.get_user_prompt("planner", context)

            # Call model
            response = self._call_model(user_prompt)
            logger.debug(f"Planner raw response: {response}")

            # Parse response
            output = self._parse_json_response(response)

            # Validate output
            if not self.validate_output(output):
                logger.warning("Planner output validation failed, creating simple plan")
                output = self._create_simple_plan(state.user_input)

            # Update state
            state.planner_output = output

            step_count = len(output.get("plan", []))
            logger.info(f"Planner created plan with {step_count} steps")

            return state

        except Exception as e:
            error_msg = f"Planner execution failed: {str(e)}"
            logger.error(error_msg)
            state.add_error(error_msg)

            # Use simple plan on failure
            state.planner_output = self._create_simple_plan(state.user_input)
            return state

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate planner output structure

        Args:
            output: Output dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_keys = ["plan"]

        if not validate_dict_structure(output, required_keys):
            return False

        # Validate plan structure
        plan = output.get("plan", [])
        if not isinstance(plan, list) or len(plan) == 0:
            return False

        # Validate each step
        for step in plan:
            if not isinstance(step, dict):
                return False
            if "action" not in step:
                return False

        return True

    def _create_simple_plan(self, user_input: str) -> Dict[str, Any]:
        """
        Create a simple fallback plan

        Args:
            user_input: Original user input

        Returns:
            Simple execution plan
        """
        return {
            "plan": [
                {
                    "step": 1,
                    "action": "Process user request directly",
                    "tool": "none",
                    "inputs": {"user_input": user_input},
                    "expected_output": "Response to user request",
                    "success_criteria": "Valid response generated"
                }
            ],
            "risks": ["Plan generation failed, using simple fallback"],
            "mitigations": ["Direct execution without complex planning"],
            "estimated_duration": "quick"
        }
