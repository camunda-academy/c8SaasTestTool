#!/bin/sh

# Camunda 8 SaaS Connection Test Tool - Shell Wrapper for Python
# This script runs the Python version of the connection test tool

# Function to print error message
print_error() {
    echo "***** CONNECTION FAILED: $1 *****"
    exit 1
}

# Check if Python 3 is available
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    # Check if python command points to Python 3
    PYTHON_VERSION=$(python -c "import sys; print(sys.version_info[0])" 2>/dev/null)
    if [ "$PYTHON_VERSION" = "3" ]; then
        PYTHON_CMD="python"
    else
        print_error "Python 3 is required but not found. Please install Python 3."
    fi
else
    print_error "Python is not installed. Please install Python 3."
fi

# Check if we're in the correct directory (should contain envVars.txt)
if [ ! -f "../envVars.txt" ] && [ ! -f "envVars.txt" ]; then
    print_error "envVars.txt file not found. Please run this script from the project root directory or python subdirectory."
fi

# Change to the python directory if we're in the root
if [ -f "envVars.txt" ] && [ -d "python" ]; then
    cd python || print_error "Cannot access python directory"
fi

# Run the Python script (all dependencies bundled in lib/)
echo "Starting Camunda 8 SaaS connection test..."
$PYTHON_CMD testConnection.py