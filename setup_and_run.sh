#!/bin/bash

# Exit immediately on error and enable pipeline error detection
set -e

# Function to install Python on different Linux distributions
install_python_linux() {
    echo "Detecting package manager..."
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        echo "Installing Python on Ubuntu/Debian..."
        sudo apt-get update -qq
        sudo apt-get install -y python3 python3-pip python3-venv
    elif command -v dnf &> /dev/null; then
        # Fedora/RHEL 8+
        echo "Installing Python on Fedora/RHEL 8+..."
        sudo dnf install -y python3 python3-pip
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL 7
        echo "Installing Python on CentOS/RHEL 7..."
        sudo yum install -y python3 python3-pip
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        echo "Installing Python on Arch Linux..."
        sudo pacman -Sy --noconfirm python python-pip
    else
        echo "Unsupported Linux distribution. Please install Python manually."
        echo "Supported package managers: apt, dnf, yum, pacman"
        exit 1
    fi
}

# Function to install Python on macOS
install_python_mac() {
    if command -v brew &> /dev/null; then
        echo "Installing Python using Homebrew..."
        brew install python
    else
        echo "Homebrew not found. Please install Homebrew first:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed."
    # Detect OS and install Python
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Linux detected."
        install_python_linux
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS detected."
        install_python_mac
    else
        echo "Unsupported operating system: $OSTYPE"
        echo "Please install Python 3.6+ manually."
        exit 1
    fi
else
    echo "Python3 is already installed: $(python3 --version)"
fi

# Verify Python installation
echo "Verifying Python installation..."
if ! python3 -c "import sys; assert sys.version_info >= (3,6)" &> /dev/null; then
    echo "Error: Python 3.6+ is required. Found: $(python3 --version)"
    exit 1
fi

# Check if venv module is available
echo "Checking venv module..."
if ! python3 -c "import venv" &> /dev/null; then
    echo "venv module not available. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y python3-venv
        fi
    fi
fi

# Create virtual environment if it doesn't exist
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists at '$VENV_DIR'."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install required dependencies
echo "Installing dependencies..."
pip install -q flask flask-cors werkzeug requests

# Verify critical dependencies
echo "Verifying critical dependencies..."
if ! python -c "import flask, flask_cors, requests" &> /dev/null; then
    echo "Error: Failed to import critical dependencies"
    deactivate
    exit 1
fi

# Check for server.py
if [ ! -f "server.py" ]; then
    echo "Error: server.py not found in current directory"
    echo "Please ensure server.py exists before running this script"
    deactivate
    exit 1
fi

# Run the server
echo "Starting server.py..."
python server.py

# Deactivate virtual environment when done
echo "Server process ended. Deactivating environment..."
deactivate