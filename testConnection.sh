#!/bin/sh

# Load the environment variables from the envVars.txt file
if [ -f "envVars.txt" ]; then
    . ./envVars.txt
else
    echo "envVars.txt file not found. Double check that this file is available in this directory (ls)"
    exit 1
fi

# Function to print error message
print_error() {
    echo "***** CONNECTION FAILED: $1"
    exit 1
}

# Generate the token
TOKEN_RESPONSE=$(curl --silent --header "Content-Type: application/json" --request POST \
    --data "{\"grant_type\":\"client_credentials\", \"audience\":\"$CAMUNDA_CONSOLE_OAUTH_AUDIENCE\", \"client_id\":\"$CAMUNDA_CONSOLE_CLIENT_ID\", \"client_secret\":\"$CAMUNDA_CONSOLE_CLIENT_SECRET\"}" \
    $CAMUNDA_OAUTH_URL)

# Extract the token from the response
TOKEN=$(echo $TOKEN_RESPONSE | sed -e 's/.*"access_token":"\([^"]*\)".*/\1/')

# Check if we got a token
if [ -z "$TOKEN" ]; then
    print_error "Failed to retrieve access token."
    exit 1
fi

# Execute the curl command with the token and store the response
# Perform the curl command and capture the HTTP status code and response body
HTTP_RESPONSE=$(curl --silent --header "Authorization: Bearer $TOKEN" \
                --write-out "HTTPSTATUS:%{http_code}" \
                $CAMUNDA_CONSOLE_BASE_URL/members)

# Extract the body and the status
BODY=$(echo "$HTTP_RESPONSE" | sed -e 's/HTTPSTATUS\:.*//g')
STATUS=$(echo "$HTTP_RESPONSE" | grep -o 'HTTPSTATUS:.*' | sed -e 's/HTTPSTATUS\://')

# Check the status code
if [ "$STATUS" -eq 200 ]; then
    # Use grep to check if the response contains "name" and "email"
    if echo "$BODY" | grep -q '"name"' && echo "$BODY" | grep -q '"email"'; then
        # If the strings "name" and "email" are found, consider it successful
        echo "***** CONNECTION SUCCESSFUL *****"
    else
        # If the strings are not found, print an error message
        print_error "Response does not contain required attributes."
    fi
else
    # If the status code is not 200, print the error message
    print_error "Status code: $STATUS Response body: $BODY"
fi