"""Executor for Windows environment (from WSL or native)."""

import subprocess
import shutil
import os
from typing import Optional, List

from .base import ExecutorInterface, ExecutorResult


class WindowsExecutor(ExecutorInterface):
    """Executes Windows commands, primarily from WSL using PowerShell."""

    def __init__(self):
        """Initialize Windows executor."""
        self.powershell_exe = self._find_powershell()

    def _find_powershell(self) -> Optional[str]:
        """Find PowerShell executable."""
        # Try to find powershell.exe in PATH
        ps_path = shutil.which("powershell.exe")
        if ps_path:
            return ps_path

        # Try common Windows path from WSL
        wsl_path = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
        if os.path.exists(wsl_path):
            return wsl_path

        # Try cmd.exe as fallback
        cmd_path = shutil.which("cmd.exe")
        if cmd_path:
            return cmd_path

        return None

    def which(self, command: str) -> Optional[str]:
        """Find command in Windows PATH using PowerShell."""
        if not self.powershell_exe:
            return None

        try:
            # Use Get-Command to find the executable
            ps_command = f"Get-Command {command} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path"

            result = subprocess.run(
                [self.powershell_exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip()
                # Convert Windows path to WSL path if needed
                if path.startswith('C:'):
                    path = '/mnt/c' + path[2:].replace('\\', '/')
                return path

        except:
            pass

        return None

    def run_command(self, command: List[str], timeout: int) -> ExecutorResult:
        """Execute command in Windows environment using PowerShell."""
        if not self.powershell_exe:
            return ExecutorResult(
                returncode=-1,
                stdout="",
                stderr="",
                error="PowerShell not found"
            )

        try:
            # Build PowerShell command
            # Join command parts, escaping as needed
            cmd_str = " ".join(command)

            result = subprocess.run(
                [self.powershell_exe, "-NoProfile", "-NonInteractive", "-Command", cmd_str],
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
        """Check if Windows PowerShell is accessible."""
        if not self.powershell_exe:
            return False

        try:
            # Try a simple PowerShell command
            result = subprocess.run(
                [self.powershell_exe, "-NoProfile", "-NonInteractive", "-Command", "Write-Output 'test'"],
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0
        except:
            return False
