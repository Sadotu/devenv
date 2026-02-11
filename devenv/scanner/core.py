"""Core scanning logic for detecting development tools"""

import subprocess
import shutil
import re
from typing import Dict, List, Optional
from pathlib import Path
import yaml


class ToolScanner:
    """Main tool scanner class"""

    def __init__(self, tools_db_path: Optional[str] = None, executor=None):
        """
        Initialize the tool scanner.

        Args:
            tools_db_path: Path to tools.yaml database file
            executor: ExecutorInterface implementation for running commands
        """
        if tools_db_path is None:
            # Use default path relative to this file
            self.tools_db_path = Path(__file__).parent.parent / 'data' / 'tools.yaml'
        else:
            self.tools_db_path = Path(tools_db_path)

        # Initialize executor (default to current environment)
        if executor is None:
            from .platforms.current import CurrentEnvironmentExecutor
            executor = CurrentEnvironmentExecutor()
        self.executor = executor

        self.tools_db = self._load_tools_database()

    def _load_tools_database(self) -> Dict:
        """Load the tools database from YAML file"""
        try:
            with open(self.tools_db_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Tools database not found at {self.tools_db_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing tools database: {e}")
            return {}

    def scan_all_tools(self, categories: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        Scan for all tools in the database.

        Args:
            categories: List of categories to scan, or None for all

        Returns:
            Dictionary mapping categories to lists of tool results
        """
        results = {}

        for category, tools in self.tools_db.items():
            if categories and category not in categories:
                continue

            results[category] = []
            for tool in tools:
                tool_result = self.scan_tool(tool)
                results[category].append(tool_result)

        return results

    def scan_tool(self, tool: Dict) -> Dict:
        """
        Scan for a single tool.

        Args:
            tool: Tool definition from database

        Returns:
            Tool result dictionary with installation status and version
        """
        name = tool['name']
        commands = tool['commands']
        version_flags = tool.get('version_flags', ['--version'])

        # Try to find the tool
        for command in commands:
            path = self.executor.which(command)
            if path:
                # Tool found, try to get version
                version = self.get_tool_version(command, version_flags)
                return {
                    'name': name,
                    'command': command,
                    'installed': True,
                    'version': version,
                    'path': path
                }

        # Tool not found
        return {
            'name': name,
            'command': commands[0] if commands else name,
            'installed': False,
            'version': None,
            'path': None
        }

    def get_tool_version(self, command: str, version_flags: List[str]) -> str:
        """
        Get the version of an installed tool.

        Args:
            command: Command to run
            version_flags: List of flags to try for version detection

        Returns:
            Version string or "unknown"
        """
        for flag in version_flags:
            try:
                result = self.executor.run_command([command, flag], timeout=3)

                # Check for executor-level errors
                if result.error:
                    continue

                if result.returncode == 0:
                    version = self._parse_version_output(result.stdout + result.stderr)
                    if version:
                        return version
            except Exception:
                continue

        return "unknown"

    def _parse_version_output(self, output: str) -> Optional[str]:
        """
        Parse version number from command output.

        Args:
            output: Command output string

        Returns:
            Parsed version string or None
        """
        # Try to find version patterns
        patterns = [
            r'(\d+\.\d+\.\d+[\w\-\.]*)',  # 1.2.3 or 1.2.3-beta
            r'v(\d+\.\d+\.\d+)',            # v1.2.3
            r'version[:\s]+(\d+\.\d+\.\d+)',  # version: 1.2.3
            r'(\d+\.\d+)',                   # 1.2 (fallback)
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)

        # If no pattern matches, try to extract first line
        first_line = output.strip().split('\n')[0]
        if len(first_line) < 100:  # Reasonable length check
            return first_line.strip()

        return None

    def get_summary_stats(self, results: Dict[str, List[Dict]]) -> Dict:
        """
        Calculate summary statistics from scan results.

        Args:
            results: Scan results dictionary

        Returns:
            Dictionary with summary statistics
        """
        total_scanned = 0
        total_installed = 0

        for category, tools in results.items():
            total_scanned += len(tools)
            total_installed += sum(1 for tool in tools if tool['installed'])

        return {
            'total_scanned': total_scanned,
            'total_installed': total_installed,
            'total_missing': total_scanned - total_installed,
            'percentage_installed': round(
                (total_installed / total_scanned * 100) if total_scanned > 0 else 0, 1
            )
        }
