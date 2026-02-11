"""Executor for MSYS2 environment."""

import subprocess
import os
from typing import Optional, List

from .base import ExecutorInterface, ExecutorResult


class MSYS2Executor(ExecutorInterface):
    """Executes commands in MSYS2 environment."""

    def __init__(self, msys2_root: str):
        """
        Initialize MSYS2 executor.

        Args:
            msys2_root: Root path to MSYS2 installation (e.g., C:\\msys64)
        """
        self.msys2_root = msys2_root
        self.bash_exe = self._find_bash_exe()
        self.msys2_path = self._build_msys2_path()

    def _find_bash_exe(self) -> Optional[str]:
        """Find bash.exe in MSYS2 installation."""
        # Convert Windows path to WSL path if needed
        root = self.msys2_root
        if root.startswith('C:'):
            root = '/mnt/c' + root[2:].replace('\\', '/')

        # Try common locations
        possible_paths = [
            os.path.join(root, "usr", "bin", "bash.exe"),
            os.path.join(root, "bin", "bash.exe"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def _build_msys2_path(self) -> str:
        """Build PATH environment for MSYS2."""
        root = self.msys2_root
        if root.startswith('C:'):
            root = '/mnt/c' + root[2:].replace('\\', '/')

        # MSYS2 typical PATH includes usr/bin, bin, mingw64/bin
        paths = [
            os.path.join(root, "mingw64", "bin"),
            os.path.join(root, "usr", "bin"),
            os.path.join(root, "bin"),
        ]

        return ":".join(paths)

    def which(self, command: str) -> Optional[str]:
        """Find command in MSYS2 PATH."""
        if not self.bash_exe:
            return None

        try:
            # Run 'which' command in MSYS2 with proper PATH
            result = subprocess.run(
                [self.bash_exe, "-c", f"PATH={self.msys2_path} which {command}"],
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
        """Execute command in MSYS2 environment."""
        if not self.bash_exe:
            return ExecutorResult(
                returncode=-1,
                stdout="",
                stderr="",
                error="MSYS2 bash executable not found"
            )

        try:
            # Build bash command with proper PATH
            cmd_str = " ".join(command)
            bash_command = f"PATH={self.msys2_path} {cmd_str}"

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
        """Check if MSYS2 is accessible."""
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
