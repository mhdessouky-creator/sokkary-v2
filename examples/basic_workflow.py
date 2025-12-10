#!/usr/bin/env python3
"""
Basic Workflow Example - Sokkary V2
Demonstrates the sequential multi-agent system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflow import AgentWorkflow
from src.utils.logger import get_logger
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from rich import print as rprint

console = Console()
logger = get_logger(__name__)


def print_section(title: str, content: str = ""):
    """Print a formatted section"""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold yellow]{title}[/bold yellow]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    if content:
        console.print(content)


def run_example_1():
    """Example 1: Simple question"""
    print_section("Example 1: Simple Question")

    # Initialize workflow
    workflow = AgentWorkflow(model_name="kimi")

    # Run workflow
    user_input = "What is the capital of France?"

    console.print(f"\n[bold green]User Input:[/bold green] {user_input}\n")

    result = workflow.run(user_input)

    # Display results
    console.print("\n[bold magenta]Final Output:[/bold magenta]")
    console.print(Panel(result["final_output"], title="Response", border_style="green"))

    console.print("\n[bold cyan]Execution History:[/bold cyan]")
    for agent in result["execution_history"]:
        console.print(f"  ✓ {agent}")

    if result["errors"]:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in result["errors"]:
            console.print(f"  ✗ {error}")


def run_example_2():
    """Example 2: Complex task"""
    print_section("Example 2: Complex Task")

    # Initialize workflow
    workflow = AgentWorkflow(model_name="kimi")

    # Run workflow
    user_input = "Create a plan to learn Python programming in 30 days"

    console.print(f"\n[bold green]User Input:[/bold green] {user_input}\n")

    result = workflow.run(user_input)

    # Display detailed results
    console.print("\n[bold magenta]Orchestrator Analysis:[/bold magenta]")
    if result["orchestrator_output"]:
        console.print(JSON(str(result["orchestrator_output"])))

    console.print("\n[bold magenta]Execution Plan:[/bold magenta]")
    if result["planner_output"]:
        plan = result["planner_output"].get("plan", [])
        for step in plan[:3]:  # Show first 3 steps
            console.print(f"\n  Step {step.get('step')}: {step.get('action')}")
            console.print(f"    Expected: {step.get('expected_output', 'N/A')}")

    console.print("\n[bold magenta]Final Output:[/bold magenta]")
    console.print(Panel(result["final_output"], title="Response", border_style="green"))


def run_streaming_example():
    """Example 3: Streaming workflow"""
    print_section("Example 3: Streaming Workflow")

    # Initialize workflow
    workflow = AgentWorkflow(model_name="kimi")

    # Run workflow with streaming
    user_input = "Explain the difference between AI and Machine Learning"

    console.print(f"\n[bold green]User Input:[/bold green] {user_input}\n")
    console.print("[bold yellow]Streaming agent outputs...[/bold yellow]\n")

    for chunk in workflow.stream(user_input):
        for node_name, node_output in chunk.items():
            if node_name != "__end__":
                current = node_output.get("current_agent", "unknown")
                console.print(f"[bold cyan]>>> {current.upper()}[/bold cyan]")

    console.print("\n[bold green]Streaming complete![/bold green]")


def show_workflow_diagram():
    """Display the workflow diagram"""
    print_section("Workflow Architecture")

    workflow = AgentWorkflow(model_name="kimi")
    console.print(workflow.get_graph_diagram())


def interactive_mode():
    """Interactive mode - chat with the agents"""
    print_section("Interactive Mode", "Type 'quit' to exit, 'diagram' to show workflow")

    workflow = AgentWorkflow(model_name="kimi")

    while True:
        console.print("\n[bold green]You:[/bold green] ", end="")
        user_input = input().strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            break

        if user_input.lower() == "diagram":
            console.print(workflow.get_graph_diagram())
            continue

        if not user_input:
            continue

        try:
            result = workflow.run(user_input)

            console.print("\n[bold magenta]Assistant:[/bold magenta]")
            console.print(Panel(result["final_output"], border_style="blue"))

            # Show which agents were used
            agents_used = " → ".join(result["execution_history"])
            console.print(f"\n[dim]Pipeline: {agents_used}[/dim]")

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}")


def main():
    """Main entry point"""
    console.print("\n[bold blue]╔═══════════════════════════════════════════════════════════╗[/bold blue]")
    console.print("[bold blue]║[/bold blue]  [bold white]Sokkary V2 - Multi-Agent Workflow Examples[/bold white]            [bold blue]║[/bold blue]")
    console.print("[bold blue]╚═══════════════════════════════════════════════════════════╝[/bold blue]\n")

    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        console.print("[bold yellow]Choose a mode:[/bold yellow]")
        console.print("  1. Example 1 - Simple question")
        console.print("  2. Example 2 - Complex task")
        console.print("  3. Example 3 - Streaming")
        console.print("  4. Show workflow diagram")
        console.print("  5. Interactive mode")
        console.print("\n[bold green]Enter choice (1-5):[/bold green] ", end="")
        mode = input().strip()

    try:
        if mode == "1":
            run_example_1()
        elif mode == "2":
            run_example_2()
        elif mode == "3":
            run_streaming_example()
        elif mode == "4":
            show_workflow_diagram()
        elif mode == "5" or mode.lower() == "interactive":
            interactive_mode()
        else:
            console.print(f"[bold red]Unknown mode: {mode}[/bold red]")
            console.print("[yellow]Usage: python basic_workflow.py [1|2|3|4|5|interactive][/yellow]")

    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]Interrupted by user[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        logger.exception("Example failed")


if __name__ == "__main__":
    main()
