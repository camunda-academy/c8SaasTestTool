# Camunda 8 SaaS Connection Test Tool - PowerShell Wrapper for Python
# This script runs the Python version of the connection test tool

# Function to print error message
Function Print-Error {
    Write-Host "***** CONNECTION FAILED: $($args[0]) *****"
    exit 1
}

# Check if Python 3 is available
$pythonCmd = $null

try {
    $python3Version = & python3 --version 2>$null
    if ($python3Version -match "Python 3\.") {
        $pythonCmd = "python3"
    }
} catch {
    # python3 command not found, try python
}

if (-not $pythonCmd) {
    try {
        $pythonVersion = & python --version 2>$null
        if ($pythonVersion -match "Python 3\.") {
            $pythonCmd = "python"
        } else {
            Print-Error "Python 3 is required but current version is: $pythonVersion"
        }
    } catch {
        Print-Error "Python is not installed. Please install Python 3."
    }
}

# Check if we're in the correct directory (should contain envVars.txt)
if (-not (Test-Path "../envVars.txt") -and -not (Test-Path "envVars.txt")) {
    Print-Error "envVars.txt file not found. Please run this script from the project root directory or python subdirectory."
}

# Change to the python directory if we're in the root
if ((Test-Path "envVars.txt") -and (Test-Path "python")) {
    Set-Location "python"
    if (-not $?) {
        Print-Error "Cannot access python directory"
    }
}

# Run the Python script (all dependencies bundled in lib/)
Write-Host "Starting Camunda 8 SaaS connection test..."
try {
    & $pythonCmd testConnection.py
} catch {
    Print-Error "Failed to execute Python script: $_"
}