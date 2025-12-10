"""
LangGraph Sequential Workflow for Sokkary V2
Coordinates the multi-agent system
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.agents.base_agent import AgentState
from src.agents.orchestrator import OrchestratorAgent
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.agents.validator import ValidatorAgent
from src.utils.logger import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


class WorkflowState(TypedDict):
    """
    State definition for LangGraph workflow
    Compatible with AgentState
    """
    user_input: str
    orchestrator_output: dict | None
    planner_output: dict | None
    executor_output: dict | None
    validator_output: dict | None
    current_agent: str | None
    execution_history: list[str]
    errors: list[str]
    available_tools: list[str]
    available_skills: list[str]
    final_output: str | None


class AgentWorkflow:
    """
    Sequential multi-agent workflow using LangGraph
    """

    def __init__(
        self,
        model_name: str | None = None,
        enable_checkpoints: bool = True
    ):
        """
        Initialize the workflow

        Args:
            model_name: Model to use for all agents (defaults to settings)
            enable_checkpoints: Enable state checkpointing
        """
        self.model_name = model_name or settings.default_model

        # Initialize agents
        logger.info(f"Initializing agents with model: {self.model_name}")

        self.orchestrator = OrchestratorAgent(model_name=self.model_name)
        self.planner = PlannerAgent(model_name=self.model_name)
        self.executor = ExecutorAgent(model_name=self.model_name)
        self.validator = ValidatorAgent(model_name=self.model_name)

        # Initialize checkpoint saver if enabled
        self.checkpointer = MemorySaver() if enable_checkpoints else None

        # Build the graph
        self.graph = self._build_graph()

        logger.info("Workflow initialized successfully")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph sequential workflow

        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(WorkflowState)

        # Add nodes (each node is an agent)
        workflow.add_node("orchestrator", self._run_orchestrator)
        workflow.add_node("planner", self._run_planner)
        workflow.add_node("executor", self._run_executor)
        workflow.add_node("validator", self._run_validator)

        # Define edges (sequential flow)
        workflow.set_entry_point("orchestrator")
        workflow.add_edge("orchestrator", "planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "validator")
        workflow.add_edge("validator", END)

        # Compile graph
        if self.checkpointer:
            compiled = workflow.compile(checkpointer=self.checkpointer)
        else:
            compiled = workflow.compile()

        logger.info("Workflow graph compiled")
        return compiled

    def _convert_to_agent_state(self, state: WorkflowState) -> AgentState:
        """
        Convert WorkflowState to AgentState

        Args:
            state: Workflow state dict

        Returns:
            AgentState instance
        """
        return AgentState(
            user_input=state["user_input"],
            orchestrator_output=state.get("orchestrator_output"),
            planner_output=state.get("planner_output"),
            executor_output=state.get("executor_output"),
            validator_output=state.get("validator_output"),
            current_agent=state.get("current_agent"),
            execution_history=state.get("execution_history", []),
            errors=state.get("errors", []),
            available_tools=state.get("available_tools", []),
            available_skills=state.get("available_skills", []),
            final_output=state.get("final_output"),
        )

    def _convert_from_agent_state(self, agent_state: AgentState) -> dict:
        """
        Convert AgentState back to dict for WorkflowState

        Args:
            agent_state: AgentState instance

        Returns:
            Dictionary compatible with WorkflowState
        """
        return {
            "user_input": agent_state.user_input,
            "orchestrator_output": agent_state.orchestrator_output,
            "planner_output": agent_state.planner_output,
            "executor_output": agent_state.executor_output,
            "validator_output": agent_state.validator_output,
            "current_agent": agent_state.current_agent,
            "execution_history": agent_state.execution_history,
            "errors": agent_state.errors,
            "available_tools": agent_state.available_tools,
            "available_skills": agent_state.available_skills,
            "final_output": agent_state.final_output,
        }

    def _run_orchestrator(self, state: WorkflowState) -> dict:
        """Run orchestrator agent"""
        logger.info("Running Orchestrator...")
        agent_state = self._convert_to_agent_state(state)
        result_state = self.orchestrator.execute(agent_state)
        return self._convert_from_agent_state(result_state)

    def _run_planner(self, state: WorkflowState) -> dict:
        """Run planner agent"""
        logger.info("Running Planner...")
        agent_state = self._convert_to_agent_state(state)
        result_state = self.planner.execute(agent_state)
        return self._convert_from_agent_state(result_state)

    def _run_executor(self, state: WorkflowState) -> dict:
        """Run executor agent"""
        logger.info("Running Executor...")
        agent_state = self._convert_to_agent_state(state)
        result_state = self.executor.execute(agent_state)
        return self._convert_from_agent_state(result_state)

    def _run_validator(self, state: WorkflowState) -> dict:
        """Run validator agent"""
        logger.info("Running Validator...")
        agent_state = self._convert_to_agent_state(state)
        result_state = self.validator.execute(agent_state)
        return self._convert_from_agent_state(result_state)

    def run(
        self,
        user_input: str,
        available_tools: list[str] | None = None,
        available_skills: list[str] | None = None,
    ) -> dict:
        """
        Run the workflow with user input

        Args:
            user_input: User's request
            available_tools: List of available tools
            available_skills: List of available skills

        Returns:
            Final workflow state
        """
        logger.info(f"Starting workflow for: {user_input[:100]}...")

        # Initialize state
        initial_state: WorkflowState = {
            "user_input": user_input,
            "orchestrator_output": None,
            "planner_output": None,
            "executor_output": None,
            "validator_output": None,
            "current_agent": None,
            "execution_history": [],
            "errors": [],
            "available_tools": available_tools or [],
            "available_skills": available_skills or [],
            "final_output": None,
        }

        try:
            # Run the graph
            result = self.graph.invoke(initial_state)

            logger.info("Workflow completed successfully")
            return result

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise

    def stream(
        self,
        user_input: str,
        available_tools: list[str] | None = None,
        available_skills: list[str] | None = None,
    ):
        """
        Stream workflow execution (yields each agent's output)

        Args:
            user_input: User's request
            available_tools: List of available tools
            available_skills: List of available skills

        Yields:
            Intermediate states as workflow progresses
        """
        logger.info(f"Streaming workflow for: {user_input[:100]}...")

        # Initialize state
        initial_state: WorkflowState = {
            "user_input": user_input,
            "orchestrator_output": None,
            "planner_output": None,
            "executor_output": None,
            "validator_output": None,
            "current_agent": None,
            "execution_history": [],
            "errors": [],
            "available_tools": available_tools or [],
            "available_skills": available_skills or [],
            "final_output": None,
        }

        try:
            # Stream the graph execution
            for chunk in self.graph.stream(initial_state):
                yield chunk

        except Exception as e:
            logger.error(f"Workflow streaming failed: {e}")
            raise

    def get_graph_diagram(self) -> str:
        """
        Get ASCII representation of the workflow graph

        Returns:
            ASCII diagram string
        """
        return """
Sokkary V2 Sequential Workflow:

┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │ ─── Analyzes complexity & routing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Planner     │ ─── Creates execution plan
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Executor     │ ─── Executes the plan
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validator     │ ─── Validates & finalizes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final Output   │
└─────────────────┘
"""
