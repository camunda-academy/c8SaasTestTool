# Camunda 8 SaaS Connection Test Tool - PowerShell Wrapper for Java
# This script runs the Java version of the connection test tool

Function Print-Error {
    Write-Host "***** CONNECTION FAILED: $($args[0]) *****"
    exit 1
}

# Check if Java is available
$javaCmd = $null

try {
    $javaVersion = & java -version 2>&1
    if ($javaVersion) {
        $javaCmd = "java"
    }
}
catch {
    Print-Error "Java is not installed. Please install Java 8 or higher."
}

# Check if JAR file exists
$jarFile = "target\testConnection.jar"
if (-not (Test-Path $jarFile)) {
    Print-Error "JAR file not found. Please run 'mvn package' first to build the project."
}

# Run the Java application
Write-Host "Starting Camunda 8 SaaS connection test..."
try {
    & $javaCmd -jar $jarFile
    exit $LASTEXITCODE
}
catch {
    Print-Error "Failed to run Java application: $_"
}
