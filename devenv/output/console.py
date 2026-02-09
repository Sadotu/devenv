"""Console output formatter with rich formatting"""

from typing import Dict, List
from datetime import datetime
import platform


class ConsoleFormatter:
    """Format scan results for console output"""

    # Category display names and icons
    CATEGORY_ICONS = {
        'package_managers': '📦',
        'languages': '🐍',
        'version_control': '🔀',
        'containers': '🐳',
        'cloud_tools': '☁️',
        'build_tools': '🔨',
        'editors': '📝',
        'shells': '🐚',
        'databases': '🗄️',
        'infrastructure': '🏗️',
        'utilities': '🔧'
    }

    CATEGORY_NAMES = {
        'package_managers': 'PACKAGE MANAGERS',
        'languages': 'LANGUAGES & RUNTIMES',
        'version_control': 'VERSION CONTROL',
        'containers': 'CONTAINERS & ORCHESTRATION',
        'cloud_tools': 'CLOUD CLI TOOLS',
        'build_tools': 'BUILD TOOLS',
        'editors': 'TEXT EDITORS & IDEs',
        'shells': 'SHELLS',
        'databases': 'DATABASES',
        'infrastructure': 'INFRASTRUCTURE AS CODE',
        'utilities': 'UTILITIES'
    }

    @staticmethod
    def format_header(environment=None):
        """Format the header"""
        output = []
        output.append("╔══════════════════════════════════════════════════════════════╗")
        output.append("║          DEVELOPMENT ENVIRONMENT SCAN REPORT                 ║")
        output.append("╚══════════════════════════════════════════════════════════════╝\n")

        if environment:
            output.append(f"Environment: {environment.get('name', 'Unknown')}")
            output.append(f"Type: {environment.get('type', 'Unknown')}")
            output.append(f"Path: {environment.get('path', 'Unknown')}")
        else:
            output.append(f"System: {platform.system()} {platform.release()}")
            output.append(f"Hostname: {platform.node()}")

        output.append(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")

        return "\n".join(output)

    @staticmethod
    def format_category(category: str, tools: List[Dict], show_missing: bool = False):
        """Format a category of tools"""
        output = []

        icon = ConsoleFormatter.CATEGORY_ICONS.get(category, '•')
        name = ConsoleFormatter.CATEGORY_NAMES.get(category, category.upper().replace('_', ' '))

        installed = [t for t in tools if t['installed']]
        missing = [t for t in tools if not t['installed']]

        output.append("━" * 64)
        output.append(f"{icon} {name} ({len(installed)} found)")
        output.append("━" * 64)

        if installed:
            for tool in installed:
                version = tool.get('version', 'unknown')
                path = tool.get('path', 'unknown')
                # Truncate long paths
                if len(path) > 40:
                    path = '...' + path[-37:]
                output.append(f"✓ {tool['name']:<20} {version:<15} {path}")

        if show_missing and missing:
            output.append("")
            for tool in missing:
                output.append(f"✗ {tool['name']:<20} (not installed)")

        output.append("")
        return "\n".join(output)

    @staticmethod
    def format_summary(stats: Dict):
        """Format summary statistics"""
        output = []
        output.append("━" * 64)
        output.append("📊 SUMMARY")
        output.append("━" * 64)
        output.append(f"Total Scanned:       {stats['total_scanned']} tools")
        output.append(f"Installed:           {stats['total_installed']} tools ({stats['percentage_installed']}%)")
        output.append(f"Not Installed:       {stats['total_missing']} tools")
        output.append("")

        return "\n".join(output)

    @staticmethod
    def format_comparison(results_by_env: Dict[str, Dict]):
        """Format cross-environment comparison"""
        output = []
        output.append("━" * 64)
        output.append("🔄 CROSS-ENVIRONMENT COMPARISON")
        output.append("━" * 64)

        env_names = list(results_by_env.keys())
        if len(env_names) < 2:
            output.append("Need at least 2 environments to compare.")
            return "\n".join(output)

        # Get all tools from all environments
        all_tools = set()
        env_tools = {}

        for env_name, results in results_by_env.items():
            tools_in_env = set()
            for category, tools in results.items():
                for tool in tools:
                    if tool['installed']:
                        tool_name = tool['name']
                        all_tools.add(tool_name)
                        tools_in_env.add(tool_name)
            env_tools[env_name] = tools_in_env

        # Calculate comparison stats
        if len(env_names) == 2:
            env1, env2 = env_names
            only_in_1 = env_tools[env1] - env_tools[env2]
            only_in_2 = env_tools[env2] - env_tools[env1]
            in_both = env_tools[env1] & env_tools[env2]

            output.append(f"Tools only in {env1}: {len(only_in_1)}")
            output.append(f"Tools only in {env2}: {len(only_in_2)}")
            output.append(f"Tools in both: {len(in_both)}")

        output.append("")
        return "\n".join(output)
