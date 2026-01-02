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
from handlers.router import Router
from tools.fpl_tool import FPLTool

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
    router = Router(gemini)

    # Initialize Tools
    fpl_tool = FPLTool()

    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Enhanced routing logic
            analysis = await router.route(user_input)

            response = ""
            agent_name = "System"
            action = analysis.get("action")
            reasoning = analysis.get("reasoning", "")

            if reasoning:
                logger.info(f"Routing decision: {action} - {reasoning}")

            if action == "code":
                print(f"⚙️  Code execution request detected: {reasoning}")

                suggested_desc = analysis.get("suggested_description", user_input)

                # Ask Gemini to generate the code based on the refined description
                code_prompt = f"Write python code for: {suggested_desc}. Only provide the code, no markdown."
                code_resp = await gemini.process_request(code_prompt)

                # Clean up code block markers if present
                code_to_run = code_resp.replace("```python", "").replace("```", "").strip()

                print(f"📄 Generated Code:\n{code_to_run}\n")
                confirm = input("Execute this code? (y/n): ")
                if confirm.lower() == 'y':
                    result = executor.execute_python(code_to_run)
                    response = f"Execution Result:\nStdout: {result.get('stdout')}\nStderr: {result.get('stderr')}"
                    agent_name = "CodeExecutor"
                else:
                    response = "Execution cancelled."

            elif action == "tool":
                tool_name = analysis.get("tool_name")
                print(f"🛠️  Tool usage detected: {tool_name}")

                if tool_name == "fpl_news":
                    response = fpl_tool.get_news()
                    agent_name = "FPL Tool"
                else:
                    response = f"Unknown tool: {tool_name}"
                    agent_name = "System"

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
