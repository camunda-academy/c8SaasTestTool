# Camunda 8 SaaS Connection Test Tool - Python

## Requirements

- **Python 3.8 or higher** (check with `python3 --version`)
- **No installation needed** - all dependencies bundled in `lib/` directory

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
python3 testConnection.py
```

**Behind a proxy:**
```bash
# Set proxy environment variables
export HTTPS_PROXY=http://proxy.example.com:8080
export HTTP_PROXY=http://proxy.example.com:8080

# With authentication:
export HTTPS_PROXY=http://username:password@proxy.example.com:8080
export HTTP_PROXY=http://username:password@proxy.example.com:8080

python3 testConnection.py
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

**"Python 3.8 or higher is required"**
- Upgrade Python from [python.org](https://www.python.org/downloads/)

**"envVars.txt file not found"**
- Ensure file exists in parent directory
- Run from `python/` subdirectory

**"Connection error" or "Timeout"**
- Check internet/proxy settings
- If behind a proxy, set: `export HTTPS_PROXY=http://proxy.example.com:8080`
- Contact training manager

**"Authentication error"**
- Verify credentials in `envVars.txt`

## Testing

```bash
python3 test_connection_unit_tests.py
```

---

## Creating a Release for Trainees

The `lib/` directory is excluded from git (bundled dependencies). To create a release:

**1. Bundle dependencies:**
```bash
mkdir -p lib
pip3 download -d lib requests
cd lib && for wheel in *.whl; do unzip -q "$wheel" -d .; done
rm *.whl *.dist-info -rf
cd ..
```

**2. Create release archive:**
```bash
cd .. && tar -czf c8-connection-test-python.tar.gz \
  python/testConnection.py \
  python/testConnection.sh \
  python/testConnection.ps1 \
  python/lib \
  python/README.md \
  envVars.txt
```

**3. Distribute `c8-connection-test-python.tar.gz` to trainees**

Trainees extract and run - no installation required!