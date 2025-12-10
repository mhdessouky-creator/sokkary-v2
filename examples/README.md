# Sokkary V2 - Examples

This directory contains usage examples for the Sokkary V2 multi-agent system.

## Available Examples

### 1. Basic Workflow (`basic_workflow.py`)

Demonstrates the core sequential workflow with all four agents.

**Usage:**

```bash
# Run interactively (choose mode)
python examples/basic_workflow.py

# Run specific examples
python examples/basic_workflow.py 1  # Simple question
python examples/basic_workflow.py 2  # Complex task
python examples/basic_workflow.py 3  # Streaming
python examples/basic_workflow.py 4  # Show diagram
python examples/basic_workflow.py 5  # Interactive mode
```

**Features:**
- Simple question answering
- Complex task planning
- Streaming agent outputs
- Interactive chat mode
- Workflow visualization

## Prerequisites

1. **Set up environment:**

```bash
# Copy and configure .env file
cp .env.template .env
nano .env  # Add your Kimi K2 API key
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

## Example Outputs

### Example 1: Simple Question

```
User Input: What is the capital of France?

Pipeline: orchestrator → planner → executor → validator

Final Output: The capital of France is Paris.
```

### Example 2: Complex Task

```
User Input: Create a plan to learn Python programming in 30 days

Orchestrator Analysis:
  Complexity: complex
  Requires Planning: true
  Routing: full_pipeline

Execution Plan:
  Step 1: Set up Python environment
  Step 2: Learn basic syntax (variables, loops, functions)
  Step 3: Practice with small projects
  ...

Final Output: [Detailed 30-day learning plan]
```

### Example 3: Streaming

Shows real-time agent execution:

```
>>> ORCHESTRATOR
>>> PLANNER
>>> EXECUTOR
>>> VALIDATOR

Streaming complete!
```

## Interactive Mode

The interactive mode allows you to chat with the multi-agent system:

```bash
python examples/basic_workflow.py 5
```

Commands:
- Type your question/request
- `diagram` - Show workflow diagram
- `quit` or `exit` - Exit

## Customization

### Using Different Models

```python
# Use Claude instead of Kimi
workflow = AgentWorkflow(model_name="claude")

# Use Groq
workflow = AgentWorkflow(model_name="groq")
```

### Providing Tools and Skills

```python
result = workflow.run(
    user_input="Your request",
    available_tools=["file_reader", "web_search"],
    available_skills=["research", "analysis"]
)
```

## Troubleshooting

**Error: "Model not available"**
- Check that your API key is configured in `.env`
- Verify the model name is supported

**Error: "Import error"**
- Make sure you're in the project root directory
- Run `pip install -r requirements.txt`

**Slow responses**
- Kimi K2 response time varies
- Consider using Groq for faster inference

## Next Steps

1. Explore the source code in `src/agents/`
2. Check the workflow implementation in `src/workflow.py`
3. Read the full documentation in `docs/`
4. Experiment with different prompts and tasks
