"""Base executor interface for cross-environment command execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ExecutorResult:
    """Result from executing a command in a target environment."""
    returncode: int
    stdout: str
    stderr: str
    error: Optional[str] = None


class ExecutorInterface(ABC):
    """Abstract interface for executing commands in different environments."""

    @abstractmethod
    def which(self, command: str) -> Optional[str]:
        """
        Find command in target environment's PATH.

        Args:
            command: Command name to locate

        Returns:
            Full path to command if found, None otherwise
        """
        pass

    @abstractmethod
    def run_command(self, command: List[str], timeout: int) -> ExecutorResult:
        """
        Execute command in target environment.

        Args:
            command: Command and arguments as list
            timeout: Maximum execution time in seconds

        Returns:
            ExecutorResult with returncode, stdout, stderr, and optional error
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if target environment is accessible.

        Returns:
            True if environment can be used, False otherwise
        """
        pass
