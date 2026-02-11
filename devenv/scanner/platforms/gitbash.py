"""Executor for Git Bash environment."""

import subprocess
import os
from typing import Optional, List

from .base import ExecutorInterface, ExecutorResult


class GitBashExecutor(ExecutorInterface):
    """Executes commands in Git Bash environment."""

    def __init__(self, git_bash_root: str):
        """
        Initialize Git Bash executor.

        Args:
            git_bash_root: Root path to Git installation (e.g., C:\\Program Files\\Git)
        """
        self.git_bash_root = git_bash_root
        self.bash_exe = self._find_bash_exe()
        self.git_bash_path = self._build_git_bash_path()

    def _find_bash_exe(self) -> Optional[str]:
        """Find bash.exe in Git installation."""
        # Convert Windows path to WSL path if needed
        root = self.git_bash_root
        if root.startswith('C:'):
            root = '/mnt/c' + root[2:].replace('\\', '/')

        # Try common locations
        possible_paths = [
            os.path.join(root, "bin", "bash.exe"),
            os.path.join(root, "usr", "bin", "bash.exe"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def _build_git_bash_path(self) -> str:
        """Build PATH environment for Git Bash."""
        root = self.git_bash_root
        if root.startswith('C:'):
            root = '/mnt/c' + root[2:].replace('\\', '/')

        # Git Bash typical PATH includes bin, usr/bin, mingw64/bin
        paths = [
            os.path.join(root, "mingw64", "bin"),
            os.path.join(root, "usr", "bin"),
            os.path.join(root, "bin"),
        ]

        return ":".join(paths)

    def which(self, command: str) -> Optional[str]:
        """Find command in Git Bash PATH."""
        if not self.bash_exe:
            return None

        try:
            # Run 'which' command in Git Bash with proper PATH
            result = subprocess.run(
                [self.bash_exe, "-c", f"PATH={self.git_bash_path} which {command}"],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()

        except:
            pass

        return None

    def run_command(self, command: List[str], timeout: int) -> ExecutorResult:
        """Execute command in Git Bash environment."""
        if not self.bash_exe:
            return ExecutorResult(
                returncode=-1,
                stdout="",
                stderr="",
                error="Git Bash executable not found"
            )

        try:
            # Build bash command with proper PATH
            cmd_str = " ".join(command)
            bash_command = f"PATH={self.git_bash_path} {cmd_str}"

            result = subprocess.run(
                [self.bash_exe, "-c", bash_command],
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
        """Check if Git Bash is accessible."""
        if not self.bash_exe:
            return False

        if not os.path.exists(self.bash_exe):
            return False

        try:
            # Try running a simple command
            result = subprocess.run(
                [self.bash_exe, "-c", "echo test"],
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0
        except:
            return False
