"""
Validator Agent - Validates execution results and provides final output
"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentState
from src.config.prompts import AgentPrompts
from src.utils.logger import get_logger
from src.utils.helpers import validate_dict_structure, safe_get

logger = get_logger(__name__)


class ValidatorAgent(BaseAgent):
    """
    Validator Agent

    Responsibilities:
    - Receive execution results from Executor
    - Validate outputs against success criteria
    - Check for errors or inconsistencies
    - Provide final quality assessment
    - Generate final output for user
    """

    def __init__(self, **kwargs):
        super().__init__(agent_type="validator", **kwargs)

    def execute(self, state: AgentState) -> AgentState:
        """
        Validate execution results and create final output

        Args:
            state: Current agent state with executor output

        Returns:
            Updated state with validator output and final_output
        """
        logger.info("Validator validating results...")

        # Update state
        state.add_to_history("validator")

        try:
            # Create context and generate prompt
            context = self._create_context(state)
            user_prompt = AgentPrompts.get_user_prompt("validator", context)

            # Call model
            response = self._call_model(user_prompt)
            logger.debug(f"Validator raw response: {response}")

            # Parse response
            output = self._parse_json_response(response)

            # Validate output structure
            if not self.validate_output(output):
                logger.warning("Validator output validation failed, creating default")
                output = self._create_default_validation(state)

            # Update state
            state.validator_output = output

            # Set final output
            state.final_output = output.get("final_output", "Validation completed")

            validation_status = output.get("validation_status", "unknown")
            quality_score = output.get("quality_score", 0)

            logger.info(
                f"Validator completed: {validation_status} "
                f"(quality: {quality_score}/100)"
            )

            return state

        except Exception as e:
            error_msg = f"Validator execution failed: {str(e)}"
            logger.error(error_msg)
            state.add_error(error_msg)

            # Create default validation
            output = self._create_default_validation(state)
            state.validator_output = output
            state.final_output = output.get("final_output")

            return state

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate validator output structure

        Args:
            output: Output dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_keys = [
            "validation_status",
            "final_output"
        ]

        if not validate_dict_structure(output, required_keys):
            return False

        # Validate status
        valid_status = output["validation_status"] in ["passed", "failed", "partial"]

        return valid_status

    def _create_default_validation(self, state: AgentState) -> Dict[str, Any]:
        """
        Create default validation when validation fails

        Args:
            state: Current agent state

        Returns:
            Default validation output
        """
        # Extract final output from executor if available
        executor_output = state.executor_output or {}
        executed_steps = executor_output.get("executed_steps", [])

        if executed_steps:
            # Get result from last successful step
            for step in reversed(executed_steps):
                if step.get("status") == "success" and step.get("result"):
                    final_output = step["result"]
                    break
            else:
                final_output = executor_output.get("summary", "Task completed")
        else:
            final_output = "Unable to generate output"

        overall_status = executor_output.get("overall_status", "unknown")

        return {
            "validation_status": "partial" if overall_status == "success" else "failed",
            "criteria_met": ["execution_completed"],
            "criteria_failed": [],
            "quality_score": 70 if overall_status == "success" else 30,
            "issues": ["Validation system used default assessment"],
            "recommendations": ["Review execution results manually"],
            "final_output": final_output
        }
