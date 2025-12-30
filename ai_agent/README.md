# Termux Multi-Agent AI

A powerful multi-agent AI system designed to run on Termux (Android), featuring GPT4Free, Google Gemini, and code execution capabilities.

## Directory Structure

```
📂 ai_agent/
├── 📂 config/          # Configuration
├── 📂 agents/          # AI Agents (G4F, Gemini, Code Executor)
├── 📂 handlers/        # Session and Export handlers
├── 📂 exports/         # Output directory
├── 📂 logs/            # Logs
├── 📂 sandbox/         # Code execution sandbox
├── .env                # Environment variables
├── setup_ai_agent.sh   # Setup script
└── main.py             # Entry point
```

## Setup

1.  **Clone the repository** (if you haven't already).
2.  **Run the setup script**:
    ```bash
    chmod +x ai_agent/setup_ai_agent.sh
    ./ai_agent/setup_ai_agent.sh
    ```
3.  **Configure Environment**:
    Edit `ai_agent/.env` and add your keys:
    ```
    API_KEY_GEMINI=your_api_key_here
    ```

## Usage

Run the main script:
```bash
python ai_agent/main.py
```

## Features

*   **Gemini Orchestrator**: Manages conversation and delegates tasks.
*   **G4F Agent**: Provides free access to LLMs.
*   **Code Executor**: Executes Python code and shell commands (use with caution!).
*   **Session Management**: Saves chat history.
*   **Export**: Export conversations and code.

## Disclaimer

This tool allows code execution. Use responsibly.
