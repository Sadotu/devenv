"""Platform executors for cross-environment command execution."""

from typing import Dict
from .base import ExecutorInterface
from .current import CurrentEnvironmentExecutor
from .wsl import WSLExecutor
from .windows import WindowsExecutor
from .gitbash import GitBashExecutor
from .msys2 import MSYS2Executor


def create_executor(env_metadata: Dict) -> ExecutorInterface:
    """
    Create appropriate executor based on environment metadata.

    Args:
        env_metadata: Dictionary with environment information including:
            - type: Environment type (wsl, windows, gitbash, msys2, current)
            - name: Environment name
            - is_current: Boolean indicating if this is the current environment
            - distro: (WSL only) Distro name
            - path: (Git Bash/MSYS2 only) Installation path

    Returns:
        ExecutorInterface implementation for the environment
    """
    # Check if this is the current environment
    if env_metadata.get('is_current', False):
        return CurrentEnvironmentExecutor()

    env_type = env_metadata.get('type', '').lower()

    if env_type == 'wsl':
        distro_name = env_metadata.get('distro', env_metadata.get('name', ''))
        return WSLExecutor(distro_name=distro_name)

    elif env_type == 'windows':
        return WindowsExecutor()

    elif env_type == 'gitbash' or env_type == 'git bash':
        git_bash_root = env_metadata.get('path', 'C:\\Program Files\\Git')
        return GitBashExecutor(git_bash_root=git_bash_root)

    elif env_type == 'msys2':
        msys2_root = env_metadata.get('path', 'C:\\msys64')
        return MSYS2Executor(msys2_root=msys2_root)

    else:
        # Default to current environment executor
        return CurrentEnvironmentExecutor()


__all__ = [
    'ExecutorInterface',
    'ExecutorResult',
    'CurrentEnvironmentExecutor',
    'WSLExecutor',
    'WindowsExecutor',
    'GitBashExecutor',
    'MSYS2Executor',
    'create_executor',
]
