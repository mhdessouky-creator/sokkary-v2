#!/usr/bin/env python3
"""
Quick test for Phase 2 implementation
Tests the basic workflow functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from src.agents.base_agent import BaseAgent, AgentState
        from src.agents.orchestrator import OrchestratorAgent
        from src.agents.planner import PlannerAgent
        from src.agents.executor import ExecutorAgent
        from src.agents.validator import ValidatorAgent
        from src.workflow import AgentWorkflow
        from src.config.settings import settings
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_settings():
    """Test settings configuration"""
    print("\nTesting settings...")
    try:
        from src.config.settings import settings

        print(f"  Default model: {settings.default_model}")
        print(f"  Available models: {settings.available_models}")
        print(f"  Kimi configured: {bool(settings.kimi_api_key)}")
        print(f"  Max tokens: {settings.max_tokens}")
        print(f"  Temperature: {settings.temperature}")
        print("✓ Settings loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False


def test_agent_initialization():
    """Test agent initialization"""
    print("\nTesting agent initialization...")
    try:
        from src.agents.orchestrator import OrchestratorAgent
        from src.agents.planner import PlannerAgent
        from src.agents.executor import ExecutorAgent
        from src.agents.validator import ValidatorAgent

        orchestrator = OrchestratorAgent(model_name="kimi")
        planner = PlannerAgent(model_name="kimi")
        executor = ExecutorAgent(model_name="kimi")
        validator = ValidatorAgent(model_name="kimi")

        print(f"  Orchestrator: {orchestrator}")
        print(f"  Planner: {planner}")
        print(f"  Executor: {executor}")
        print(f"  Validator: {validator}")
        print("✓ All agents initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_initialization():
    """Test workflow initialization"""
    print("\nTesting workflow initialization...")
    try:
        from src.workflow import AgentWorkflow

        workflow = AgentWorkflow(model_name="kimi")
        print(f"  Workflow created with model: {workflow.model_name}")
        print(f"  Graph compiled: {workflow.graph is not None}")
        print("✓ Workflow initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Workflow initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_diagram():
    """Test workflow diagram generation"""
    print("\nTesting workflow diagram...")
    try:
        from src.workflow import AgentWorkflow

        workflow = AgentWorkflow(model_name="kimi")
        diagram = workflow.get_graph_diagram()
        print(diagram)
        print("✓ Diagram generated successfully")
        return True
    except Exception as e:
        print(f"✗ Diagram generation failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Phase 2 Integration Tests")
    print("="*60)

    tests = [
        test_imports,
        test_settings,
        test_agent_initialization,
        test_workflow_initialization,
        test_workflow_diagram,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test crashed: {e}")
            results.append(False)

    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*60)

    if all(results):
        print("\n✅ All tests passed! Phase 2 is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
