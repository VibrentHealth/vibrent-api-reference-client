#!/bin/bash

# Vibrent Health API Client - Java Runner Script
# This script builds and runs the Java implementation

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JAVA_DIR="$SCRIPT_DIR/java"
JAR_FILE="$JAVA_DIR/target/vibrent-api-client-1.0.0.jar"

echo "🚀 Vibrent Health API Client - Java Implementation"
echo "=================================================="

# Function to check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check if Maven is installed
    if ! command -v mvn &> /dev/null; then
        echo "❌ Error: Maven is not installed or not in PATH"
        echo "   Please install Maven 3.6 or higher"
        exit 1
    fi
    
    # Check Java version
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
    if [ "$JAVA_VERSION" -lt 11 ]; then
        echo "❌ Error: Java 11 or higher is required (found Java $JAVA_VERSION)"
        exit 1
    fi
    
    echo "✅ Java version: $(java -version 2>&1 | head -n 1)"
    echo "✅ Maven version: $(mvn -version | head -n 1)"
    echo ""
}

# Function to build the project
build_project() {
    echo "🔨 Building Java project..."
    echo "   Working directory: $JAVA_DIR"
    echo ""
    
    cd "$JAVA_DIR"
    
    # Clean and build
    echo "🧹 Cleaning previous build..."
    mvn clean
    
    echo "🔨 Building project..."
    mvn package
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Build successful!"
        echo "📦 JAR file created at: $JAR_FILE"
        echo ""
    else
        echo ""
        echo "❌ Build failed!"
        exit 1
    fi
    
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
    echo "🚀 Starting Java application..."
    echo ""
    
    if [ ! -f "$JAR_FILE" ]; then
        echo "❌ JAR file not found at: $JAR_FILE"
        echo "   Building project first..."
        build_project
    fi
    
    # Run the application with any provided arguments
    if [ $# -eq 0 ]; then
        # No arguments - use default config
        echo "📝 Using default configuration"
        java -jar "$JAR_FILE"
    else
        # Pass arguments to the application
        echo "📝 Using custom arguments: $*"
        java -jar "$JAR_FILE" "$@"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS] [JAVA_ARGS...]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -b, --build    Build the project only (don't run)"
    echo "  -r, --run      Run the application only (skip build if JAR exists)"
    echo "  --force-build  Force rebuild even if JAR exists"
    echo ""
    echo "Examples:"
    echo "  $0                    # Build and run with default config"
    echo "  $0 --build            # Build only"
    echo "  $0 --run              # Run only (if JAR exists)"
    echo "  $0 custom_config.yaml # Build and run with custom config"
    echo ""
    echo "Environment Variables:"
    echo "  VIBRENT_CLIENT_ID     Your Vibrent Health client ID"
    echo "  VIBRENT_CLIENT_SECRET Your Vibrent Health client secret"
    echo "  VIBRENT_ENVIRONMENT   Environment (staging/production)"
    echo ""
}

# Parse command line arguments
BUILD_ONLY=false
RUN_ONLY=false
FORCE_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -b|--build)
            BUILD_ONLY=true
            shift
            ;;
        -r|--run)
            RUN_ONLY=true
            shift
            ;;
        --force-build)
            FORCE_BUILD=true
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

if [ "$BUILD_ONLY" = true ]; then
    build_project
    echo "✅ Build completed successfully!"
elif [ "$RUN_ONLY" = true ]; then
    if [ ! -f "$JAR_FILE" ]; then
        echo "❌ JAR file not found. Use --force-build or run without --run flag"
        exit 1
    fi
    run_application "$@"
else
    # Default: build and run
    if [ "$FORCE_BUILD" = true ] || [ ! -f "$JAR_FILE" ]; then
        build_project
    else
        echo "📦 JAR file found, skipping build"
        echo ""
    fi
    run_application "$@"
fi 