#!/bin/sh

# Camunda 8 SaaS Connection Test Tool - Shell Wrapper for Java
# This script runs the Java version of the connection test tool

print_error() {
    echo "***** CONNECTION FAILED: $1 *****"
    exit 1
}

# Check if Java is available
if command -v java >/dev/null 2>&1; then
    JAVA_CMD="java"
else
    print_error "Java is not installed. Please install Java 8 or higher."
fi

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | awk -F '.' '{print $1}')
if [ "$JAVA_VERSION" -lt 17 ] && [ "$JAVA_VERSION" != "1" ]; then
    print_error "Java 17 or higher is required. Please upgrade Java."
fi

# Check if JAR file exists
JAR_FILE="target/testConnection.jar"
if [ ! -f "$JAR_FILE" ]; then
    print_error "JAR file not found. Please run 'mvn package' first to build the project."
fi

# Change to the java directory if we're in the root
if [ -f "envVars.txt" ] && [ -d "java" ]; then
    cd java || print_error "Cannot access java directory"
    JAR_FILE="target/testConnection.jar"
fi

# Run the Java application
echo "Starting Camunda 8 SaaS connection test..."
$JAVA_CMD -jar "$JAR_FILE"
