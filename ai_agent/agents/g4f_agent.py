import g4f
import logging
import asyncio

class G4FAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Default to a robust provider/model if possible, or let g4f decide
        self.provider = g4f.Provider.Bing

    async def generate_response(self, prompt: str) -> str:
        """
        Generates a response using G4F (GPT4Free).
        """
        try:
            self.logger.info("Generating response with G4F...")

            # Note: g4f API usage might vary with versions.
            # This is a standard async implementation pattern.
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": prompt}],
            )

            return response
        except Exception as e:
            self.logger.error(f"G4F Agent Error: {e}")
            return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test
    agent = G4FAgent()
    print(asyncio.run(agent.generate_response("Hello, are you working?")))
