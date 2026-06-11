#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
ROOT_DIR="$(dirname "$DIR")"
VENV_DIR="$ROOT_DIR/.venv"

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
else
    VENV_PYTHON="$VENV_DIR/bin/python"
fi

if [ ! -x "$VENV_PYTHON" ]; then
    PYTHON_CMD=""
    if command -v python3 > /dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python > /dev/null 2>&1; then
        PYTHON_CMD="python"
    fi
    if [ -z "$PYTHON_CMD" ]; then
        echo "Error: Python is required but not installed." >&2
        exit 1
    fi
    if ! "$PYTHON_CMD" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
        echo "Error: Python 3.10 or higher is required." >&2
        exit 1
    fi
    echo "Creating virtual environment in $VENV_DIR..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
fi

echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

if [ -f "$ROOT_DIR/pyproject.toml" ]; then
    echo "Installing project and dev requirements from pyproject.toml..."
    # Install the project in editable mode with dev dependencies
    (cd "$ROOT_DIR" && "$VENV_PYTHON" -m pip install -e ".[dev]")
else
    echo "No pyproject.toml found."
fi

echo "Virtual environment is ready. To activate, run:"
echo "source .venv/bin/activate"
