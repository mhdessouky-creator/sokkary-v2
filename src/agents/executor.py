"""
Executor Agent - Executes the plan using available tools
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent, AgentState
from src.config.prompts import AgentPrompts
from src.utils.logger import get_logger
from src.utils.helpers import validate_dict_structure, safe_get

logger = get_logger(__name__)


class ExecutorAgent(BaseAgent):
    """
    Executor Agent

    Responsibilities:
    - Receive execution plan from Planner
    - Execute each step using available tools
    - Handle errors and retries
    - Collect results and evidence
    """

    def __init__(self, **kwargs):
        super().__init__(agent_type="executor", **kwargs)
        self.max_retries = 3

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute the plan step by step

        Args:
            state: Current agent state with planner output

        Returns:
            Updated state with executor output
        """
        logger.info("Executor starting execution...")

        # Update state
        state.add_to_history("executor")

        try:
            # Get plan from state
            plan = safe_get(state.planner_output, "plan", [])

            if not plan:
                logger.warning("No plan found, creating direct response")
                return self._direct_execution(state)

            # Execute each step
            executed_steps = []
            overall_status = "success"

            for step in plan:
                step_result = self._execute_step(step, state)
                executed_steps.append(step_result)

                # Update overall status
                if step_result["status"] == "failure":
                    overall_status = "failure"
                elif step_result["status"] == "partial" and overall_status != "failure":
                    overall_status = "partial"

            # Create output
            output = {
                "executed_steps": executed_steps,
                "overall_status": overall_status,
                "summary": self._create_summary(executed_steps, overall_status)
            }

            # Validate output
            if not self.validate_output(output):
                logger.warning("Executor output validation failed")

            # Update state
            state.executor_output = output

            logger.info(f"Executor completed with status: {overall_status}")

            return state

        except Exception as e:
            error_msg = f"Executor execution failed: {str(e)}"
            logger.error(error_msg)
            state.add_error(error_msg)

            # Create error output
            state.executor_output = {
                "executed_steps": [],
                "overall_status": "failure",
                "summary": f"Execution failed: {str(e)}"
            }
            return state

    def _execute_step(self, step: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """
        Execute a single step from the plan

        Args:
            step: Step dictionary from plan
            state: Current agent state

        Returns:
            Step execution result
        """
        step_num = step.get("step", 0)
        action = step.get("action", "unknown")

        logger.info(f"Executing step {step_num}: {action}")

        try:
            # Create execution prompt
            context = self._create_context(state)
            context["current_step"] = step

            user_prompt = f"""Execute this step:

Step {step_num}: {action}
Tool: {step.get('tool', 'none')}
Inputs: {step.get('inputs', {})}

Provide the result of executing this step."""

            # Call model to execute step
            response = self._call_model(user_prompt)

            return {
                "step": step_num,
                "action": action,
                "tool_used": step.get("tool", "none"),
                "result": response,
                "status": "success",
                "evidence": f"Completed: {action}",
                "error": None
            }

        except Exception as e:
            logger.error(f"Step {step_num} failed: {e}")
            return {
                "step": step_num,
                "action": action,
                "tool_used": step.get("tool", "none"),
                "result": None,
                "status": "failure",
                "evidence": None,
                "error": str(e)
            }

    def _direct_execution(self, state: AgentState) -> AgentState:
        """
        Direct execution when no plan is available

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        logger.info("Performing direct execution")

        try:
            # Create context
            context = self._create_context(state)
            user_prompt = AgentPrompts.get_user_prompt("executor", context)

            # Call model
            response = self._call_model(user_prompt)

            # Create output
            output = {
                "executed_steps": [
                    {
                        "step": 1,
                        "action": "Direct response generation",
                        "tool_used": "none",
                        "result": response,
                        "status": "success",
                        "evidence": "Direct execution completed",
                        "error": None
                    }
                ],
                "overall_status": "success",
                "summary": "Direct execution completed successfully"
            }

            state.executor_output = output
            return state

        except Exception as e:
            error_msg = f"Direct execution failed: {str(e)}"
            logger.error(error_msg)
            state.add_error(error_msg)

            state.executor_output = {
                "executed_steps": [],
                "overall_status": "failure",
                "summary": error_msg
            }
            return state

    def _create_summary(self, executed_steps: List[Dict], status: str) -> str:
        """
        Create execution summary

        Args:
            executed_steps: List of executed steps
            status: Overall status

        Returns:
            Summary string
        """
        total_steps = len(executed_steps)
        successful = sum(1 for s in executed_steps if s["status"] == "success")
        failed = sum(1 for s in executed_steps if s["status"] == "failure")

        return (
            f"Executed {total_steps} steps. "
            f"Successful: {successful}, Failed: {failed}. "
            f"Overall status: {status}"
        )

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate executor output structure

        Args:
            output: Output dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_keys = ["executed_steps", "overall_status", "summary"]

        if not validate_dict_structure(output, required_keys):
            return False

        # Validate status
        valid_status = output["overall_status"] in ["success", "partial", "failure"]

        return valid_status
