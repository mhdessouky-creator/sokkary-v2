from typing import Optional, List
from src.agents.base import BaseAgent
from src.core.state import SharedState, TaskStatus

class Orchestrator(BaseAgent):
    def __init__(self, name: str = "Orchestrator", model_client=None, tools=None):
        super().__init__(name, model_client, tools)
        self.planner: Optional[BaseAgent] = None
        self.executor: Optional[BaseAgent] = None
        self.validator: Optional[BaseAgent] = None

    def set_agents(self, planner: BaseAgent, executor: BaseAgent, validator: BaseAgent):
        """Sets the sub-agents for the orchestration loop."""
        self.planner = planner
        self.executor = executor
        self.validator = validator

    async def process(self, state: SharedState) -> SharedState:
        """
        The main loop. It routes execution between Planner -> Executor -> Validator.
        """
        self.log_thought(f"Starting orchestration for task: {state.task_id}")
        state.status = TaskStatus.IN_PROGRESS

        if not self.planner or not self.executor or not self.validator:
            self.log_thought("Agents not initialized properly.")
            state.status = TaskStatus.FAILED
            return state

        # 1. Planning Phase
        if not state.plan:
            self.log_thought("Requesting plan from Planner...")
            state = await self.planner.process(state)
            if not state.plan:
                self.log_thought("Planner failed to generate a plan.")
                state.status = TaskStatus.FAILED
                return state

        # 2. Execution Loop
        while state.current_step_index < len(state.plan):
            current_step = state.get_current_step()
            self.log_thought(f"Executing step {state.current_step_index + 1}/{len(state.plan)}: {current_step}")

            # Execute
            state = await self.executor.process(state)

            # Validate
            self.log_thought("Validating execution...")
            state = await self.validator.process(state)

            if state.status == TaskStatus.FAILED:
                 self.log_thought("Task failed during execution/validation.")
                 return state

            # If the validator didn't advance the step (retry logic could be here),
            # we need to ensure we don't loop infinitely without progress.
            # For now, we assume the validator handles step increment or failure.
            # If the validator is just checking and passing, it should increment the index.

            # Check if completed
            if state.status == TaskStatus.COMPLETED:
                break

        if state.status != TaskStatus.FAILED:
            state.status = TaskStatus.COMPLETED
            self.log_thought("Orchestration completed successfully.")

        return state
