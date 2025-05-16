# Check if the envVars.txt file exists
if (-Not (Test-Path "envVars.txt")) {
    Write-Host "envVars.txt file not found. Double check that this file is available in this directory."
    exit
}

# Load the environment variables from the envVars.txt file
Get-Content "envVars.txt" | ForEach-Object {
    if ($_ -match "export\s+(\w+)='(.+)'") {
        Set-Item -Path "env:$($matches[1])" -Value $matches[2]
    }
}

# Function to print error message
Function Print-Error {
    Write-Host "***** CONNECTION FAILED: $($args[0]) *****"
    exit
}

# Generate the token
$tokenRequestBody = @{
    grant_type = "client_credentials"
    audience = $env:CAMUNDA_CONSOLE_OAUTH_AUDIENCE
    client_id = $env:CAMUNDA_CONSOLE_CLIENT_ID
    client_secret = $env:CAMUNDA_CONSOLE_CLIENT_SECRET
} | ConvertTo-Json

try {
    $tokenResponse = Invoke-RestMethod -Uri $env:CAMUNDA_OAUTH_URL -Method Post -ContentType "application/json" -Body $tokenRequestBody -ErrorAction Stop
    $accessToken = $tokenResponse.access_token
} catch {
    Print-Error "Failed to retrieve access token. $_"
}

# Check if we got a token
if (-not $accessToken) {
    Print-Error "Access token is null or empty."
}

# Use the token to make the next request
$headers = @{
    Authorization = "Bearer $accessToken"
}

try {
    $membersResponse = Invoke-WebRequest -Uri "$env:CAMUNDA_CONSOLE_BASE_URL/members" -Method Get -Headers $headers
    $membersStatus = $membersResponse.StatusCode
} catch {
    Print-Error "HTTP request failed. $_"
}

# Check the status code
if ($membersStatus -eq 200) {
    $membersBody = $membersResponse.Content

    # Check if the response contains "name" and "email"
    if ($membersBody -match '"name":' -and $membersBody -match '"email":') {
        # If the strings "name" and "email" are found, consider it successful
        Write-Host "***** CONNECTION SUCCESSFUL *****"
    } else {
        # If the strings are not found, print an error message
        Print-Error "Response does not contain required attributes."
    }
} else {
    # If the status code is not 200 or if the response is empty, print the error message
    Print-Error "Status code: $membersStatus Response body: $membersBody"
}