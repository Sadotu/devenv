# Installation Instructions for DevEnv

## Prerequisites

DevEnv requires:
- Python 3.7 or higher
- PyYAML library

## Installation Methods

### Method 1: Using pip (Recommended)

```bash
cd /mnt/c/Users/nickd/DevProjects/devenv
pip install -e .
```

After installation, you can run `devenv` from anywhere:
```bash
devenv
```

### Method 2: Install pip first (if needed)

If you don't have pip installed:

**On Ubuntu/Debian/WSL:**
```bash
sudo apt update
sudo apt install python3-pip python3-yaml
```

**On macOS:**
```bash
brew install python3
```

**On Windows:**
```
python -m ensurepip
```

Then follow Method 1.

### Method 3: Run without installation (Quick Start)

You can run devenv directly without installing:

```bash
cd /mnt/c/Users/nickd/DevProjects/devenv

# Make sure PyYAML is available
python3 -c "import yaml" 2>/dev/null || pip install --user PyYAML

# Run directly
python3 -m devenv
```

### Method 4: Create a symbolic link (Unix/Linux/macOS/WSL)

```bash
cd /mnt/c/Users/nickd/DevProjects/devenv

# Make the wrapper script executable
chmod +x devenv-run.sh

# Create a symbolic link in your local bin directory
mkdir -p ~/.local/bin
ln -s "$(pwd)/devenv-run.sh" ~/.local/bin/devenv

# Make sure ~/.local/bin is in your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Now you can run `devenv` from anywhere!

### Method 5: Add alias (Temporary solution)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias devenv='python3 /mnt/c/Users/nickd/DevProjects/devenv/devenv/cli.py'
```

Then reload your shell:
```bash
source ~/.bashrc
```

## Verify Installation

Test that devenv is working:

```bash
devenv --list-environments
```

You should see a list of detected development environments.

## Troubleshooting

### "command not found: devenv"

Make sure:
1. You've followed one of the installation methods above
2. Your PATH includes the installation directory
3. You've reloaded your shell configuration

### "No module named yaml"

Install PyYAML:
```bash
pip install --user PyYAML
```

Or:
```bash
sudo apt install python3-yaml  # Ubuntu/Debian
```

### "Permission denied"

On Unix systems, make the script executable:
```bash
chmod +x devenv-run.sh
```

## Uninstallation

If installed with pip:
```bash
pip uninstall devenv
```

If using symbolic link:
```bash
rm ~/.local/bin/devenv
```

If using alias, remove the line from your `~/.bashrc` or `~/.zshrc`.
