import subprocess
import os
import logging
import sys
from config.config import Config

class CodeExecutor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sandbox_dir = Config.SANDBOX_DIR

        if not os.path.exists(self.sandbox_dir):
            os.makedirs(self.sandbox_dir)

    def execute_python(self, code: str, filename: str = "script.py") -> dict:
        """
        Executes Python code in the sandbox directory.
        """
        file_path = os.path.join(self.sandbox_dir, filename)

        try:
            # Write code to file
            with open(file_path, "w") as f:
                f.write(code)

            self.logger.info(f"Executing Python script: {file_path}")

            # Execute
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                cwd=self.sandbox_dir,
                timeout=30  # Safety timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            self.logger.error("Execution timed out.")
            return {"success": False, "error": "Execution timed out (30s limit)"}
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_shell(self, command: str) -> dict:
        """
        Executes a shell command. Use with caution!
        """
        self.logger.info(f"Executing shell command: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.sandbox_dir,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
