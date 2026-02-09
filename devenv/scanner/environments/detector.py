"""Environment detection module - detects all available development environments"""

import platform
import os
import subprocess
from typing import List, Dict, Optional


def detect_environments() -> List[Dict]:
    """
    Detect all available development environments on the system.

    Returns:
        List of environment dictionaries with metadata
    """
    environments = []

    # Always add current environment
    current = {
        'name': 'Current',
        'type': get_os_type(),
        'path': os.getcwd(),
        'is_current': True,
        'shell': get_current_shell()
    }
    environments.append(current)

    # Windows-specific: Check for WSL, Git Bash, MSYS2
    if platform.system() == 'Windows':
        wsl_distros = detect_wsl_distros()
        environments.extend(wsl_distros)

        # Check for Git Bash
        git_bash_path = r'C:\Program Files\Git'
        if os.path.exists(git_bash_path):
            environments.append({
                'name': 'Git Bash',
                'type': 'gitbash',
                'path': git_bash_path,
                'is_current': False,
                'shell': 'bash'
            })

        # Check for MSYS2
        msys2_path = r'C:\msys64'
        if os.path.exists(msys2_path):
            environments.append({
                'name': 'MSYS2',
                'type': 'msys2',
                'path': msys2_path,
                'is_current': False,
                'shell': 'bash'
            })

    return environments


def detect_wsl_distros() -> List[Dict]:
    """Detect all WSL distributions"""
    try:
        result = subprocess.run(
            ['wsl', '--list', '--verbose'],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-16-le'  # WSL outputs in UTF-16 LE
        )

        distros = []
        lines = result.stdout.split('\n')

        for line in lines[1:]:  # Skip header
            line = line.strip()
            if not line:
                continue

            # Remove asterisk and split
            parts = line.replace('*', '').split()
            if len(parts) >= 2:
                name = parts[0]
                state = parts[1] if len(parts) > 1 else 'Unknown'
                version = parts[2] if len(parts) > 2 else '1'

                if state in ['Running', 'Stopped']:
                    distros.append({
                        'name': f'WSL: {name}',
                        'type': 'wsl',
                        'distro': name,
                        'wsl_version': version,
                        'state': state,
                        'path': f'\\\\wsl$\\{name}',
                        'is_current': False,
                        'shell': 'bash'
                    })

        return distros
    except (subprocess.TimeoutExpired, FileNotFoundError, UnicodeDecodeError):
        return []


def get_os_type() -> str:
    """Get the operating system type"""
    system = platform.system()

    if system == 'Windows':
        # Check if running in WSL
        if is_wsl():
            return 'wsl'
        return 'windows'
    elif system == 'Linux':
        if is_wsl():
            return 'wsl'
        return 'linux'
    elif system == 'Darwin':
        return 'macos'
    else:
        return 'unknown'


def is_wsl() -> bool:
    """Check if currently running in WSL"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
    except FileNotFoundError:
        return False


def get_current_shell() -> str:
    """Get the current shell"""
    shell = os.environ.get('SHELL', '')
    if shell:
        return os.path.basename(shell)

    # Windows fallback
    if platform.system() == 'Windows':
        if os.environ.get('PSModulePath'):
            return 'powershell'
        return 'cmd'

    return 'unknown'


def get_env_icon(env_type: str) -> str:
    """Get emoji icon for environment type"""
    icons = {
        'windows': '🪟',
        'linux': '🐧',
        'macos': '🍎',
        'wsl': '🐧',
        'docker': '🐳',
        'gitbash': '🔧',
        'msys2': '🔧'
    }
    return icons.get(env_type, '💻')


def prompt_environment_selection(environments: List[Dict]) -> List[Dict]:
    """
    Interactive prompt for environment selection.

    Args:
        environments: List of detected environments

    Returns:
        List of selected environments to scan
    """
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║           DETECTED DEVELOPMENT ENVIRONMENTS                  ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print(f"Found {len(environments)} environment(s) on this system:\n")

    for i, env in enumerate(environments, 1):
        current_marker = " ⭐ CURRENT" if env['is_current'] else ""
        icon = get_env_icon(env['type'])
        print(f" [{i}] {icon} {env['name']}{current_marker}")
        print(f"     Path: {env['path']}")
        if 'shell' in env:
            print(f"     Shell: {env['shell']}")
        if 'state' in env:
            print(f"     State: {env['state']}")
        print()

    print("Which environment(s) would you like to scan?")
    print("  [A] All environments")
    for i in range(len(environments)):
        print(f"  [{i+1}] {environments[i]['name']} only")
    print("  [C] Custom selection (multiple)\n")

    choice = input("Your choice: ").strip().upper()

    if choice == 'A':
        return environments
    elif choice.isdigit() and 1 <= int(choice) <= len(environments):
        return [environments[int(choice) - 1]]
    elif choice == 'C':
        selected = input("Enter numbers separated by commas (e.g., 1,3): ")
        try:
            indices = [int(x.strip()) - 1 for x in selected.split(',')]
            return [environments[i] for i in indices if 0 <= i < len(environments)]
        except ValueError:
            print("Invalid input. Scanning current environment only.")
            return [env for env in environments if env['is_current']]
    else:
        print("Invalid choice. Scanning current environment only.")
        return [env for env in environments if env['is_current']]
