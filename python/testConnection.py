#!/usr/bin/env python3
"""
Camunda 8 SaaS Connection Test Tool - Python Version

This tool tests connectivity to Camunda 8 SaaS by:
1. Checking Python version (must be 3.8+)
2. Loading environment variables from envVars.txt
3. Obtaining OAuth token
4. Testing API connection
5. Validating response content

All dependencies are bundled in the lib/ directory.

Author: Camunda Academy
"""

import sys
import os
import json
import re
from typing import Dict, Tuple

# Add bundled libraries to path
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
if os.path.exists(lib_path) and lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# Exit codes
EXIT_SUCCESS = 0
EXIT_SSL_ERROR = 1
EXIT_CONNECTION_ERROR = 2
EXIT_AUTH_ERROR = 3
EXIT_OTHER_ERROR = 4

# Import requests from bundled libraries
try:
    import requests
except ImportError:
    print("***** ERROR: Required 'requests' library not found *****")
    print("This package should include bundled dependencies.")
    print("Please contact your training manager.")
    sys.exit(EXIT_OTHER_ERROR)


def check_python_version() -> None:
    version_info = sys.version_info
    if version_info < (3, 8):
        print_error(
            f"Python 3.8 or higher is required. Current version: {version_info.major}.{version_info.minor}.{version_info.micro}\n"
            "Please upgrade Python or contact your training manager.\n"
            "Download Python from: https://www.python.org/downloads/"
        )
        sys.exit(EXIT_OTHER_ERROR)
    print(f"Python version check passed: {version_info.major}.{version_info.minor}.{version_info.micro}")


def print_error(message: str) -> None:
    print(f"***** CONNECTION FAILED: {message} *****")


def print_success() -> None:
    print("***** CONNECTION SUCCESSFUL *****")


def load_env_vars(file_path: str = "envVars.txt") -> Dict[str, str]:
    if not os.path.isfile(file_path):
        parent_file_path = os.path.join("..", file_path)
        if os.path.isfile(parent_file_path):
            file_path = parent_file_path
        else:
            raise FileNotFoundError(f"{file_path} file not found. Double check that this file is available in this directory or parent directory")
    
    env_vars = {}
    
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                match = re.match(r"export\s+(\w+)='(.+)'", line)
                if match:
                    var_name, var_value = match.groups()
                    env_vars[var_name] = var_value
                else:
                    raise ValueError(f"Invalid format in {file_path} at line {line_num}: {line}")
    
    except Exception as e:
        raise ValueError(f"Error reading {file_path}: {str(e)}")
    
    required_vars = [
        'CAMUNDA_CONSOLE_CLIENT_ID',
        'CAMUNDA_CONSOLE_CLIENT_SECRET',
        'CAMUNDA_OAUTH_URL',
        'CAMUNDA_CONSOLE_BASE_URL',
        'CAMUNDA_CONSOLE_OAUTH_AUDIENCE'
    ]
    
    missing_vars = [var for var in required_vars if var not in env_vars]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return env_vars


def get_access_token(env_vars: Dict[str, str]) -> str:
    token_request_data = {
        "grant_type": "client_credentials",
        "audience": env_vars['CAMUNDA_CONSOLE_OAUTH_AUDIENCE'],
        "client_id": env_vars['CAMUNDA_CONSOLE_CLIENT_ID'],
        "client_secret": env_vars['CAMUNDA_CONSOLE_CLIENT_SECRET']
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            env_vars['CAMUNDA_OAUTH_URL'],
            json=token_request_data,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        token_response = response.json()
        access_token = token_response.get('access_token')
        
        if not access_token:
            raise ValueError("Access token not found in response")
        
        return access_token
        
    except Exception as e:
        if hasattr(e, '__class__') and 'requests' in str(e.__class__):
            if 'SSL' in str(e):
                raise Exception(f"SSL certificate error: {str(e)}")
            elif 'Connection' in str(e):
                raise Exception(f"Connection error: {str(e)}")
            elif 'Timeout' in str(e):
                raise Exception(f"Request timeout: {str(e)}")
            elif 'HTTP' in str(e):
                raise Exception(f"HTTP error {response.status_code}: {response.text}")
            else:
                raise Exception(f"Request error: {str(e)}")
        elif isinstance(e, json.JSONDecodeError):
            raise Exception(f"Invalid JSON response: {str(e)}")
        else:
            raise e


def test_api_connection(env_vars: Dict[str, str], access_token: str) -> Tuple[int, str]:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    api_url = f"{env_vars['CAMUNDA_CONSOLE_BASE_URL']}/members"
    
    try:
        response = requests.get(
            api_url,
            headers=headers,
            timeout=30
        )
        
        return response.status_code, response.text
        
    except Exception as e:
        if hasattr(e, '__class__') and 'requests' in str(e.__class__):
            if 'SSL' in str(e):
                raise Exception(f"SSL certificate error: {str(e)}")
            elif 'Connection' in str(e):
                raise Exception(f"Connection error: {str(e)}")
            elif 'Timeout' in str(e):
                raise Exception(f"Request timeout: {str(e)}")
            else:
                raise Exception(f"Request error: {str(e)}")
        else:
            raise e


def validate_response(status_code: int, response_body: str) -> bool:
    if status_code != 200:
        print_error(f"Status code: {status_code} Response body: {response_body}")
        return False
    
    if '"name"' in response_body and '"email"' in response_body:
        return True
    else:
        print_error("Response does not contain required attributes.")
        return False


def main() -> None:
    try:
        check_python_version()
        
        print("Loading environment variables...")
        env_vars = load_env_vars()
        
        print("Requesting access token...")
        access_token = get_access_token(env_vars)
        
        print("Testing API connection...")
        status_code, response_body = test_api_connection(env_vars, access_token)
        
        if validate_response(status_code, response_body):
            print_success()
            sys.exit(EXIT_SUCCESS)
        else:
            sys.exit(EXIT_OTHER_ERROR)
        
    except FileNotFoundError as e:
        print_error(str(e))
        sys.exit(EXIT_OTHER_ERROR)
    except ValueError as e:
        error_msg = str(e).lower()
        if "token" in error_msg or "access_token" in error_msg or "authentication" in error_msg or "unauthorized" in error_msg:
            print_error(f"Authentication failed: {str(e)}")
            sys.exit(EXIT_AUTH_ERROR)
        else:
            print_error(str(e))
            sys.exit(EXIT_OTHER_ERROR)
    except Exception as e:
        error_msg = str(e).lower()
        
        if "ssl" in error_msg or "certificate" in error_msg:
            print_error(f"SSL error: {str(e)}")
            sys.exit(EXIT_SSL_ERROR)
        elif "connection" in error_msg or "proxy" in error_msg or "network" in error_msg:
            print_error(f"Connection error: {str(e)}")
            sys.exit(EXIT_CONNECTION_ERROR)
        elif "timeout" in error_msg or "timed out" in error_msg:
            print_error(f"Connection error (timeout): {str(e)}")
            sys.exit(EXIT_CONNECTION_ERROR)
        elif "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg or "forbidden" in error_msg or "authentication" in error_msg or "token" in error_msg:
            print_error(f"Authentication error: {str(e)}")
            sys.exit(EXIT_AUTH_ERROR)
        else:
            print_error(f"Unexpected error: {str(e)}")
            sys.exit(EXIT_OTHER_ERROR)


if __name__ == "__main__":
    main()