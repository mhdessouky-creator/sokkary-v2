import asyncio
import logging
import sys
import os

# Ensure we can import modules from local directories
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from agents.g4f_agent import G4FAgent
from agents.gemini_orchestrator import GeminiOrchestrator
from agents.code_executor import CodeExecutor
from handlers.session_manager import SessionManager
from handlers.export_handler import ExportHandler

# Setup logging
Config.setup_logging()
logger = logging.getLogger("Main")

async def main():
    print("🤖 Termux Multi-Agent AI Initialized")
    Config.validate()

    # Initialize components
    gemini = GeminiOrchestrator()
    g4f_agent = G4FAgent()
    executor = CodeExecutor()
    session = SessionManager()
    exporter = ExportHandler()

    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Simple routing logic (can be enhanced)
            # 1. Ask Gemini to analyze intent
            analysis = await gemini.analyze_task(user_input)

            response = ""
            agent_name = "System"

            if analysis.get("action") == "code":
                print("⚙️  Detecting code execution request...")

                # Extract code from the initial analysis
                code_to_run = analysis.get("code", "")

                if not code_to_run:
                    # Fallback if code wasn't provided in the analysis
                    print("⚠️ Code not found in analysis. Requesting code generation...")
                    code_prompt = f"Write python code for: {user_input}. Only provide the code, no markdown."
                    code_resp = await gemini.process_request(code_prompt)
                    code_to_run = code_resp

                # Clean up code block markers if present
                code_to_run = code_to_run.replace("```python", "").replace("```", "").strip()

                print(f"📄 Generated Code:\n{code_to_run}\n")

                # If there's an accompanying response, show it
                if analysis.get("response"):
                     print(f"🤖 Gemini: {analysis.get('response')}\n")

                confirm = input("Execute this code? (y/n): ")
                if confirm.lower() == 'y':
                    result = executor.execute_python(code_to_run)
                    response = f"Execution Result:\nStdout: {result.get('stdout')}\nStderr: {result.get('stderr')}"
                    agent_name = "CodeExecutor"
                else:
                    response = "Execution cancelled."

            else:
                # Chat with Gemini or fallback to G4F
                if gemini.configured:
                    context = session.get_context_for_gemini()
                    response = await gemini.process_request(user_input, history=context)
                    agent_name = "Gemini"
                else:
                    print("⚠️  Gemini not configured, falling back to G4F...")
                    response = await g4f_agent.generate_response(user_input)
                    agent_name = "G4F"

            print(f"\n🤖 {agent_name}: {response}")

            # Save interaction
            session.add_interaction(user_input, response, agent_name)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run setup_ai_agent.sh to install dependencies.")
