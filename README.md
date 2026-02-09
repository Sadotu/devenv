# DevEnv 🔍

**Development Environment Scanner** - Know exactly what tools you have installed across all your environments!

## 🎯 Why DevEnv?

Ever wondered:
- "Why did `npm` work yesterday but not today?"
- "I swear I installed Python... where did it go?"
- "Why does this work in my terminal but not in my IDE?"

**DevEnv** is your Development Environment Detective that:
- ✅ Shows you **exactly what tools** you have installed
- ✅ Reveals **where they're located** on your system
- ✅ Explains **which environment** they belong to (WSL? Windows? Both?)
- ✅ Helps you understand **why sometimes tools "disappear"**
- ✅ Gives you **confidence** about what's on your machine

No more guessing. No more frustration. Just clear visibility into your development environment.

## 📦 Installation

### Quick Install (Pip)

```bash
pip install -e .
```

### From Source

```bash
git clone https://github.com/yourusername/devenv.git
cd devenv
pip install -e .
```

## 🚀 Usage

### Basic Scan

```bash
# Interactive scan with environment selection
devenv

# Scan current environment only (fast)
devenv --current-only

# List all detected environments
devenv --list-environments
```

### Filtering

```bash
# Scan only specific categories
devenv --category languages,containers

# Show only installed tools
devenv --installed-only

# Show only missing tools
devenv --missing-only
```

### Output Formats

```bash
# Pretty console output (default)
devenv

# JSON output
devenv --format json

# CSV output
devenv --format csv

# Save to file
devenv --format json --output my-environment.json
```

### Advanced Usage

```bash
# Verbose output with progress
devenv --verbose

# Scan all environments (skip prompt)
devenv --env all

# Compare multiple environments
devenv --env all --format console
```

## 📊 Example Output

```
╔══════════════════════════════════════════════════════════════╗
║          DEVELOPMENT ENVIRONMENT SCAN REPORT                 ║
╚══════════════════════════════════════════════════════════════╝

Environment: Current
Type: wsl
Path: /home/user
Scan Date: 2026-02-09 12:34:56

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 PACKAGE MANAGERS (8 found)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ npm                10.2.3         /usr/bin/npm
✓ pip                23.1.2         /usr/bin/pip3
✓ yarn               1.22.19        /usr/bin/yarn
✓ cargo              1.75.0         ~/.cargo/bin/cargo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐍 LANGUAGES & RUNTIMES (12 found)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Python             3.11.4         /usr/bin/python3
✓ Node.js            20.11.0        /usr/bin/node
✓ Go                 1.22.0         /usr/local/go/bin/go
✓ Rust               1.75.0         ~/.cargo/bin/rustc

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Scanned:       147 tools
Installed:           52 tools (35.4%)
Not Installed:       95 tools
```

## 🎨 Features

- **Multi-Environment Detection**: Automatically detects Windows, WSL, Git Bash, MSYS2
- **300+ Tools**: Scans for hundreds of common development tools
- **Smart Version Detection**: Automatically extracts version numbers
- **Multiple Output Formats**: Console, JSON, CSV
- **Cross-Platform**: Works on Windows, Linux, macOS, WSL
- **Fast**: Completes in seconds
- **No Dependencies**: Pure Python with minimal requirements

## 📚 Tool Categories

DevEnv scans for tools in these categories:
- 📦 Package Managers (npm, pip, yarn, cargo, etc.)
- 🐍 Languages & Runtimes (Python, Node, Go, Rust, etc.)
- 🔀 Version Control (git, svn, etc.)
- 🐳 Containers (docker, kubectl, helm, etc.)
- ☁️ Cloud Tools (aws, az, gcloud, etc.)
- 🔨 Build Tools (make, cmake, webpack, etc.)
- 📝 Editors (vim, code, emacs, etc.)
- 🐚 Shells (bash, zsh, fish, powershell, etc.)
- 🗄️ Databases (mysql, postgres, mongo, etc.)
- 🏗️ Infrastructure (terraform, ansible, etc.)
- 🔧 Utilities (curl, jq, tmux, etc.)

## 🛠️ Development

```bash
# Clone the repository
git clone https://github.com/yourusername/devenv.git
cd devenv

# Install in development mode
pip install -e .

# Run directly
python -m devenv
```

## 📝 Configuration

Create `~/.devenv-config.yaml` for custom settings:

```yaml
# Default environment to scan
default_environment: current

# Categories to always scan
default_categories:
  - languages
  - package_managers
  - version_control

# Output preferences
output:
  show_paths: true
  colorize: true
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Inspired by the comprehensive TODO document for creating a development environment scanner.

## 📮 Support

- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/devenv/issues)
- Email: your.email@example.com

---

Made with 💚 for developers who want clarity in their development environment
