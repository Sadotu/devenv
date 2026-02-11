"""Executor for WSL (Windows Subsystem for Linux) environments."""

import subprocess
import shutil
from typing import Optional, List

from .base import ExecutorInterface, ExecutorResult


class WSLExecutor(ExecutorInterface):
    """Executes commands in WSL distros using wsl.exe."""

    def __init__(self, distro_name: str):
        """
        Initialize WSL executor for a specific distro.

        Args:
            distro_name: Name of the WSL distro (e.g., "Ubuntu", "Debian")
        """
        self.distro_name = distro_name
        self.wsl_exe = self._find_wsl_exe()

    def _find_wsl_exe(self) -> Optional[str]:
        """Find wsl.exe in the system."""
        # Try common locations
        wsl_path = shutil.which("wsl.exe")
        if wsl_path:
            return wsl_path

        # Try Windows System32 path from WSL
        windows_path = "/mnt/c/Windows/System32/wsl.exe"
        try:
            result = subprocess.run(
                [windows_path, "--status"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return windows_path
        except:
            pass

        return None

    def which(self, command: str) -> Optional[str]:
        """Find command in WSL distro's PATH."""
        if not self.wsl_exe:
            return None

        try:
            result = subprocess.run(
                [self.wsl_exe, "-d", self.distro_name, "-e", "which", command],
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
        """Execute command in WSL distro."""
        if not self.wsl_exe:
            return ExecutorResult(
                returncode=-1,
                stdout="",
                stderr="",
                error="wsl.exe not found"
            )

        try:
            # Build wsl.exe command: wsl -d <distro> -e <command> <args...>
            wsl_command = [self.wsl_exe, "-d", self.distro_name, "-e"] + command

            result = subprocess.run(
                wsl_command,
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
        """Check if WSL distro is available and running/stopped."""
        if not self.wsl_exe:
            return False

        try:
            # Check distro status using wsl --list --verbose
            result = subprocess.run(
                [self.wsl_exe, "--list", "--verbose"],
                capture_output=True,
                timeout=5
            )

            # Handle UTF-16 LE encoding
            try:
                output = result.stdout.decode('utf-16-le')
            except:
                output = result.stdout.decode('utf-8', errors='ignore')

            # Check if distro is in the list and is Running or Stopped
            # (we skip Installing, Uninstalling states)
            for line in output.split('\n'):
                if self.distro_name in line:
                    # Check for Running or Stopped state
                    if 'Running' in line or 'Stopped' in line:
                        return True
                    break

            return False
        except:
            return False
