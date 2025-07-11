#!/bin/bash

# Vibrent Health API Client - Python Runner Script
# This script sets up and runs the Python implementation

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/python"
PYTHON_SCRIPT="$PYTHON_DIR/run_export.py"

echo "🐍 Vibrent Health API Client - Python Implementation"
echo "==================================================="

# Function to check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        echo "❌ Error: Python 3 is not installed or not in PATH"
        echo "   Please install Python 3.7 or higher"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
        echo "❌ Error: Python 3.7 or higher is required (found Python $PYTHON_VERSION)"
        exit 1
    fi
    
    echo "✅ Python version: $(python3 --version)"
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        echo "❌ Error: pip3 is not installed or not in PATH"
        echo "   Please install pip3"
        exit 1
    fi
    
    echo "✅ pip3 version: $(pip3 --version)"
    echo ""
}

# Function to setup virtual environment
setup_venv() {
    echo "🔧 Setting up Python environment..."
    
    cd "$PYTHON_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Python environment setup complete!"
    echo ""
    
    cd "$SCRIPT_DIR"
}

# Function to check environment variables
check_environment() {
    echo "🔍 Checking environment variables..."
    
    if [ -z "$VIBRENT_CLIENT_ID" ] || [ -z "$VIBRENT_CLIENT_SECRET" ]; then
        echo "⚠️  Warning: VIBRENT_CLIENT_ID and/or VIBRENT_CLIENT_SECRET not set"
        echo "   Make sure to set these environment variables or create a .env file"
        echo "   Example:"
        echo "     export VIBRENT_CLIENT_ID=\"your_client_id\""
        echo "     export VIBRENT_CLIENT_SECRET=\"your_client_secret\""
        echo "     export VIBRENT_ENVIRONMENT=\"staging\""
        echo ""
    else
        echo "✅ Environment variables are set"
        echo ""
    fi
}

# Function to run the application
run_application() {
    echo "🚀 Starting Python application..."
    echo ""
    
    cd "$PYTHON_DIR"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run the application with any provided arguments
    if [ $# -eq 0 ]; then
        # No arguments - use default config
        echo "📝 Using default configuration"
        python run_export.py
    else
        # Pass arguments to the application
        echo "📝 Using custom arguments: $*"
        python run_export.py "$@"
    fi
    
    cd "$SCRIPT_DIR"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS] [PYTHON_ARGS...]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -s, --setup    Setup Python environment only (don't run)"
    echo "  -r, --run      Run the application only (skip setup if venv exists)"
    echo "  --force-setup  Force recreate virtual environment"
    echo ""
    echo "Examples:"
    echo "  $0                    # Setup and run with default config"
    echo "  $0 --setup            # Setup only"
    echo "  $0 --run              # Run only (if venv exists)"
    echo "  $0 custom_config.yaml # Setup and run with custom config"
    echo ""
    echo "Environment Variables:"
    echo "  VIBRENT_CLIENT_ID     Your Vibrent Health client ID"
    echo "  VIBRENT_CLIENT_SECRET Your Vibrent Health client secret"
    echo "  VIBRENT_ENVIRONMENT   Environment (staging/production)"
    echo ""
}

# Function to check if virtual environment exists
venv_exists() {
    [ -d "$PYTHON_DIR/venv" ] && [ -f "$PYTHON_DIR/venv/bin/activate" ]
}

# Parse command line arguments
SETUP_ONLY=false
RUN_ONLY=false
FORCE_SETUP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--setup)
            SETUP_ONLY=true
            shift
            ;;
        -r|--run)
            RUN_ONLY=true
            shift
            ;;
        --force-setup)
            FORCE_SETUP=true
            shift
            ;;
        -*)
            echo "❌ Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Main execution
check_prerequisites
check_environment

if [ "$SETUP_ONLY" = true ]; then
    setup_venv
    echo "✅ Setup completed successfully!"
elif [ "$RUN_ONLY" = true ]; then
    if ! venv_exists; then
        echo "❌ Virtual environment not found. Use --force-setup or run without --run flag"
        exit 1
    fi
    run_application "$@"
else
    # Default: setup and run
    if [ "$FORCE_SETUP" = true ] || ! venv_exists; then
        setup_venv
    else
        echo "🐍 Virtual environment found, skipping setup"
        echo ""
    fi
    run_application "$@"
fi 