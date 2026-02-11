"""Command-line interface for devenv tool scanner"""

import argparse
import sys
import json
from typing import Optional, List

from .scanner.core import ToolScanner
from .scanner.environments.detector import (
    detect_environments,
    prompt_environment_selection
)
from .output.console import ConsoleFormatter


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='🔍 DevEnv - Development Environment Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  devenv                              # Interactive scan with environment selection
  devenv --current-only               # Scan current environment only
  devenv --list-environments          # List all detected environments
  devenv --category languages         # Scan only languages
  devenv --installed-only             # Show only installed tools
  devenv --format json                # Output as JSON
        """
    )

    # Environment selection
    env_group = parser.add_argument_group('Environment Selection')
    env_group.add_argument(
        '--list-environments',
        action='store_true',
        help='List all detected environments and exit'
    )
    env_group.add_argument(
        '--current-only',
        action='store_true',
        help='Only scan current environment (skip prompt)'
    )
    env_group.add_argument(
        '--env',
        type=str,
        help='Specify environment to scan (e.g., windows, wsl:ubuntu, all)'
    )

    # Filtering
    filter_group = parser.add_argument_group('Filtering')
    filter_group.add_argument(
        '--category',
        type=str,
        help='Comma-separated list of categories to scan (e.g., languages,containers)'
    )
    filter_group.add_argument(
        '--installed-only',
        action='store_true',
        help='Only show installed tools'
    )
    filter_group.add_argument(
        '--missing-only',
        action='store_true',
        help='Only show missing tools'
    )

    # Output
    output_group = parser.add_argument_group('Output')
    output_group.add_argument(
        '--format',
        choices=['console', 'json', 'csv'],
        default='console',
        help='Output format (default: console)'
    )
    output_group.add_argument(
        '--output',
        type=str,
        help='Output file path (default: stdout)'
    )
    output_group.add_argument(
        '--verbose',
        action='store_true',
        help='Show verbose output'
    )

    args = parser.parse_args()

    try:
        # Detect environments
        environments = detect_environments()

        # Handle --list-environments
        if args.list_environments:
            print_environments(environments)
            return 0

        # Select environments to scan
        selected_envs = select_environments(environments, args)

        # Parse categories
        categories = None
        if args.category:
            categories = [c.strip() for c in args.category.split(',')]

        # Import executor factory
        from .scanner.platforms import create_executor

        # Scan selected environments
        results_by_env = {}
        for env in selected_envs:
            if args.verbose:
                print(f"\nScanning environment: {env['name']}...")

            # Create environment-specific executor
            executor = create_executor(env)

            # Check if environment is available
            if not executor.is_available():
                print(f"Warning: Environment '{env['name']}' is not available. Skipping...")
                continue

            # Create scanner with environment-specific executor
            scanner = ToolScanner(executor=executor)

            try:
                results = scanner.scan_all_tools(categories=categories)
                results_by_env[env['name']] = results
            except Exception as e:
                print(f"Error scanning {env['name']}: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                continue

        # Format and output results (use a default scanner for stats)
        # Create a scanner for the current environment just for stats calculation
        default_scanner = ToolScanner()
        output_results(results_by_env, selected_envs, args, default_scanner)

        return 0

    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def select_environments(environments: List, args):
    """Select which environments to scan based on args"""
    if args.current_only:
        return [env for env in environments if env['is_current']]

    if args.env:
        if args.env == 'all':
            return environments
        # TODO: Implement specific environment selection
        return environments

    # Interactive selection
    if len(environments) > 1:
        return prompt_environment_selection(environments)
    else:
        return environments


def print_environments(environments: List):
    """Print list of detected environments"""
    formatter = ConsoleFormatter()
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║           DETECTED DEVELOPMENT ENVIRONMENTS                  ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print(f"Found {len(environments)} environment(s):\n")

    for i, env in enumerate(environments, 1):
        from .scanner.environments.detector import get_env_icon
        current = " ⭐" if env['is_current'] else ""
        icon = get_env_icon(env['type'])
        print(f"{i}. {icon} {env['name']}{current}")
        print(f"   Type: {env['type']}")
        print(f"   Path: {env['path']}")
        if 'shell' in env:
            print(f"   Shell: {env['shell']}")
        print()


def output_results(results_by_env: dict, selected_envs: List, args, scanner: ToolScanner):
    """Format and output scan results"""
    formatter = ConsoleFormatter()
    output_lines = []

    if args.format == 'console':
        # Console output
        for env in selected_envs:
            env_name = env['name']
            results = results_by_env[env_name]

            # Header
            output_lines.append(formatter.format_header(env))

            # Categories
            for category, tools in results.items():
                # Filter based on args
                if args.installed_only:
                    tools = [t for t in tools if t['installed']]
                elif args.missing_only:
                    tools = [t for t in tools if not t['installed']]

                if tools:  # Only show non-empty categories
                    output_lines.append(
                        formatter.format_category(
                            category,
                            tools,
                            show_missing=not args.installed_only
                        )
                    )

            # Summary
            stats = scanner.get_summary_stats(results)
            output_lines.append(formatter.format_summary(stats))

        # Cross-environment comparison
        if len(selected_envs) > 1:
            output_lines.append(formatter.format_comparison(results_by_env))

        output_text = "\n".join(output_lines)

    elif args.format == 'json':
        # JSON output
        output_data = {
            'environments': [],
            'scan_metadata': {
                'environments_scanned': len(selected_envs)
            }
        }

        for env in selected_envs:
            env_name = env['name']
            results = results_by_env[env_name]

            env_data = {
                'name': env_name,
                'type': env['type'],
                'path': env['path'],
                'tools': results,
                'statistics': scanner.get_summary_stats(results)
            }
            output_data['environments'].append(env_data)

        output_text = json.dumps(output_data, indent=2)

    else:  # CSV
        output_text = format_csv(results_by_env, selected_envs)

    # Output to file or stdout
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"\nResults written to {args.output}")
    else:
        print(output_text)


def format_csv(results_by_env: dict, selected_envs: List) -> str:
    """Format results as CSV"""
    lines = ["environment,category,name,installed,version,path"]

    for env in selected_envs:
        env_name = env['name']
        results = results_by_env[env_name]

        for category, tools in results.items():
            for tool in tools:
                lines.append(
                    f"{env_name},{category},{tool['name']},"
                    f"{tool['installed']},{tool.get('version', '')},"
                    f"{tool.get('path', '')}"
                )

    return "\n".join(lines)


if __name__ == '__main__':
    sys.exit(main())
