#!/usr/bin/env bash
# Wrapper script to run devenv without installation

# Get the actual directory where this script is located (resolve symlinks)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$SCRIPT_DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# Change to the script directory and run devenv module
cd "$SCRIPT_DIR" && python3 -m devenv.cli "$@"
