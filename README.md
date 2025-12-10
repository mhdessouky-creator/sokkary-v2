# 🤖 Sokkary V2 - AI Multi-Agent System

**Advanced multi-agent system powered by LangGraph, featuring MCP integration, dynamic tools, and extensible skills.**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/langchain-1.1.3-green.svg)](https://python.langchain.com/)
[![LangGraph](https://img.shields.io/badge/langgraph-1.0.4-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🌟 Features

### **Core Capabilities**
- ✅ **Sequential Multi-Agent Workflow** - Reliable, debuggable agent collaboration
- ✅ **Model Context Protocol (MCP)** - Advanced context management
- ✅ **Dynamic Tool System** - Extensible tool framework
- ✅ **Skill Modules** - Reusable agent capabilities
- ✅ **Multi-Model Support** - Kimi K2, Claude, Groq, OpenAI
- ✅ **State Management** - Persistent agent state with checkpoints
- ✅ **LangSmith Integration** - Full observability and debugging

### **Agent Types**
1. **Orchestrator Agent** - Analyzes tasks and routes to appropriate agents
2. **Planner Agent** - Creates detailed execution plans
3. **Executor Agent** - Executes actions and tool calls
4. **Validator Agent** - Validates outputs and ensures quality

---

## 📁 Project Structure

```
sokkary-v2/
├── src/
│   ├── agents/          # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── orchestrator.py
│   │   ├── planner.py
│   │   ├── executor.py
│   │   └── validator.py
│   ├── tools/           # Tool definitions
│   │   ├── __init__.py
│   │   ├── base_tool.py
│   │   ├── file_tools.py
│   │   ├── web_tools.py
│   │   └── code_tools.py
│   ├── skills/          # Skill modules
│   │   ├── __init__.py
│   │   ├── base_skill.py
│   │   ├── research.py
│   │   ├── analysis.py
│   │   └── generation.py
│   ├── mcp/             # Model Context Protocol
│   │   ├── __init__.py
│   │   ├── context_manager.py
│   │   └── model_router.py
│   ├── config/          # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── prompts.py
│   └── utils/           # Utilities
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── tests/               # Test suite
├── docs/                # Documentation
├── examples/            # Usage examples
├── .env.template        # Environment template
├── requirements.txt     # Dependencies
├── setup.py            # Package setup
└── README.md           # This file
```

---

## 🚀 Quick Start

### **1. Clone the Repository**

```bash
git clone https://github.com/mhdessouky-creator/sokkary-v2.git
cd sokkary-v2
```

### **2. Set Up Environment**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.template .env

# Edit .env and add your API keys
nano .env
```

### **3. Run Example**

```bash
# Coming in Phase 2
python examples/basic_workflow.py
```

---

## 📋 Development Phases

### **✅ Phase 1: Foundation & Repository Setup** (CURRENT)
- [x] Create GitHub repository
- [x] Initialize project structure
- [x] Set up configuration system
- [x] Create documentation framework
- [ ] Set up branching strategy

### **⏳ Phase 2: Core Multi-Agent Architecture**
- [ ] Implement base agent class
- [ ] Create orchestrator agent
- [ ] Create planner agent
- [ ] Create executor agent
- [ ] Create validator agent
- [ ] Implement state management
- [ ] Add agent communication protocol

### **⏳ Phase 3: MCP Integration**
- [ ] Implement context manager
- [ ] Create model router
- [ ] Add multi-model support
- [ ] Implement fallback mechanisms
- [ ] Add context caching

### **⏳ Phase 4: Tools & Skills**
- [ ] Define tool interface
- [ ] Implement file tools
- [ ] Implement web tools
- [ ] Implement code tools
- [ ] Create skill modules
- [ ] Add skill registry

### **⏳ Phase 5: Testing & Documentation**
- [ ] Write unit tests
- [ ] Create integration tests
- [ ] Add usage examples
- [ ] Complete documentation
- [ ] Create deployment guide

---

## 🏗️ Architecture

### **Sequential Agent Workflow**

```
User Input → Orchestrator → Planner → Executor → Validator → Output
                ↑                                      ↓
                └──────────── Feedback Loop ───────────┘
```

### **State Flow**

```python
{
    "input": "User's request",
    "plan": "Execution plan from planner",
    "actions": ["List of actions from executor"],
    "results": ["Results from each action"],
    "validation": "Validation report",
    "output": "Final output to user"
}
```

---

## 🔧 Configuration

All configuration is done via environment variables in `.env`:

```bash
# Primary model (pre-configured)
KIMI_API_KEY=your-kimi-api-key
DEFAULT_MODEL=kimi

# Optional models (add as needed)
ANTHROPIC_API_KEY=your-claude-api-key
GROQ_API_KEY=your-groq-api-key

# Agent settings
AGENT_TIMEOUT=60
MAX_AGENT_RETRIES=3

# MCP settings
MCP_ENABLED=true
MCP_CONTEXT_SIZE=8192
```

---

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)** - System design and patterns
- **[Agent Guide](docs/agents.md)** - How to create and use agents
- **[Tool Guide](docs/tools.md)** - Creating custom tools
- **[Skill Guide](docs/skills.md)** - Building skill modules
- **[MCP Guide](docs/mcp.md)** - Model Context Protocol usage
- **[API Reference](docs/api.md)** - Complete API documentation

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents.py
```

---

## 🤝 Contributing

This is a private project. Contributions are by invitation only.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Related Projects

- **[SOSO Multi-Agent System](../SOSO-Multi-Agent-System)** - Previous version (V1)
- **[LangChain](https://github.com/langchain-ai/langchain)** - Framework for LLM apps
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Agent workflows

---

## 📞 Support

For issues and questions, contact the project maintainer.

---

**Built with ❤️ using LangGraph and Claude Code**

*Last Updated: December 10, 2025*
