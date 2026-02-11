"""Executor for the current environment (where Python is running)."""

import shutil
import subprocess
from typing import Optional, List

from .base import ExecutorInterface, ExecutorResult


class CurrentEnvironmentExecutor(ExecutorInterface):
    """Executes commands in the current Python process's environment."""

    def which(self, command: str) -> Optional[str]:
        """Find command using shutil.which() in current PATH."""
        return shutil.which(command)

    def run_command(self, command: List[str], timeout: int) -> ExecutorResult:
        """Execute command using subprocess.run() in current environment."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return ExecutorResult(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
        except subprocess.TimeoutExpired as e:
            return ExecutorResult(
                returncode=-1,
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else "",
                error=f"Command timed out after {timeout} seconds"
            )
        except FileNotFoundError as e:
            return ExecutorResult(
                returncode=-1,
                stdout="",
                stderr="",
                error=f"Command not found: {e}"
            )
        except Exception as e:
            return ExecutorResult(
                returncode=-1,
                stdout="",
                stderr="",
                error=str(e)
            )

    def is_available(self) -> bool:
        """Current environment is always available."""
        return True
