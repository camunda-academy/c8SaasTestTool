# Camunda 8 SaaS Connection Test Tool - Java

## Requirements

- **Java 17 or higher** (check with `java -version`)
- **Maven 3.x** (for building the project)
- **Internet connection** (Maven will download Camunda client and dependencies during build)

## Build

Build the project (this will download all required dependencies):

```bash
mvn clean package
```

This creates `target/testConnection.jar` - a fat JAR with all dependencies bundled.

## Usage

**Mac/Linux:**
```bash
./testConnection.sh
```

**Windows:**
```powershell
.\testConnection.ps1
```

**Direct:**
```bash
java -jar target/testConnection.jar
```

**Behind a proxy:**
```bash
java -Dhttps.proxyHost=proxy.example.com -Dhttps.proxyPort=8080 -jar target/testConnection.jar

# With authentication:
java -Dhttps.proxyHost=proxy.example.com -Dhttps.proxyPort=8080 \
     -Dhttps.proxyUser=username -Dhttps.proxyPassword=password \
     -jar target/testConnection.jar
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | SSL Error |
| 2 | Connection Error |
| 3 | Authentication Error |
| 4 | Other Error |

## Troubleshooting

**"Java 17 or higher is required"**
- Upgrade Java from [adoptium.net](https://adoptium.net/)

**"envVarsExtended.txt file not found"**
- Ensure file exists in current or parent directory
- File must contain: CAMUNDA_CLUSTER_ID, CAMUNDA_CLIENT_ID, CAMUNDA_CLIENT_SECRET, CAMUNDA_CLUSTER_REGION

**"JAR file not found"**
- Run `mvn package` to build the project first

**"Connection error" or "Timeout"**
- Check internet/proxy settings
- If behind a proxy, use: `java -Dhttps.proxyHost=proxy.example.com -Dhttps.proxyPort=8080 -jar target/testConnection.jar`
- Contact training manager

**"Authentication error"**
- Verify credentials in `envVarsExtended.txt`

Trainees extract and run with:
- Mac/Linux: `./testConnection.sh`
- Windows: `.	estConnection.ps1`
