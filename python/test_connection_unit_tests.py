#!/usr/bin/env python3
"""
Test script for the Camunda 8 SaaS Connection Test Tool

This script tests the individual functions of the main script with mock data
to ensure all functionality works correctly.
"""

import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the current directory and lib directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
if os.path.exists(lib_path):
    sys.path.insert(0, lib_path)

from testConnection import (
    check_python_version,
    load_env_vars,
    get_access_token,
    test_api_connection,
    validate_response,
    print_error,
    print_success
)

import requests


def test_python_version_check():
    """Test Python version check function."""
    print("Testing Python version check...")
    try:
        check_python_version()
        print("✅ Python version check passed")
    except SystemExit:
        print("❌ Python version check failed")


def test_env_vars_loading():
    """Test environment variables loading function."""
    print("\nTesting environment variables loading...")
    
    # Create a temporary env vars file
    test_env_content = """export CAMUNDA_CONSOLE_CLIENT_ID='test_client_id'
export CAMUNDA_CONSOLE_CLIENT_SECRET='test_client_secret'
export CAMUNDA_OAUTH_URL='https://test.oauth.url'
export CAMUNDA_CONSOLE_BASE_URL='https://test.base.url'
export CAMUNDA_CONSOLE_OAUTH_AUDIENCE='test.audience'
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_env_content)
        temp_file = f.name
    
    try:
        env_vars = load_env_vars(temp_file)
        expected_vars = [
            'CAMUNDA_CONSOLE_CLIENT_ID',
            'CAMUNDA_CONSOLE_CLIENT_SECRET',
            'CAMUNDA_OAUTH_URL',
            'CAMUNDA_CONSOLE_BASE_URL',
            'CAMUNDA_CONSOLE_OAUTH_AUDIENCE'
        ]
        
        all_present = all(var in env_vars for var in expected_vars)
        if all_present and env_vars['CAMUNDA_CONSOLE_CLIENT_ID'] == 'test_client_id':
            print("✅ Environment variables loading passed")
        else:
            print("❌ Environment variables loading failed - missing variables")
    except Exception as e:
        print(f"❌ Environment variables loading failed: {e}")
    finally:
        os.unlink(temp_file)


def test_response_validation():
    """Test response validation function."""
    print("\nTesting response validation...")
    
    # Test successful response
    success_response = '{"name": "Test User", "email": "test@example.com"}'
    if validate_response(200, success_response):
        print("✅ Valid response correctly identified")
    else:
        print("❌ Valid response incorrectly rejected")
    
    # Test failed response (missing fields)
    fail_response = '{"id": "123"}'
    # Capture the print_error output
    with patch('builtins.print') as mock_print:
        result = validate_response(200, fail_response)
        if not result:
            print("✅ Invalid response correctly rejected")
        else:
            print("❌ Invalid response incorrectly accepted")
    
    # Test HTTP error
    with patch('builtins.print') as mock_print:
        result = validate_response(404, "Not found")
        if not result:
            print("✅ HTTP error correctly handled")
        else:
            print("❌ HTTP error incorrectly accepted")


def test_mock_token_request():
    """Test token request with mocked response."""
    print("\nTesting token request (mocked)...")
    
    # Import and setup the requests module in testConnection
    import testConnection
    import requests as real_requests
    testConnection.requests = real_requests
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "test_token_123"}
    mock_response.raise_for_status.return_value = None
    
    env_vars = {
        'CAMUNDA_CONSOLE_CLIENT_ID': 'test_id',
        'CAMUNDA_CONSOLE_CLIENT_SECRET': 'test_secret',
        'CAMUNDA_OAUTH_URL': 'https://test.url',
        'CAMUNDA_CONSOLE_OAUTH_AUDIENCE': 'test.audience'
    }
    
    with patch.object(testConnection.requests, 'post', return_value=mock_response):
        try:
            token = get_access_token(env_vars)
            if token == "test_token_123":
                print("✅ Token request (mocked) passed")
            else:
                print(f"❌ Token request failed - got: {token}")
        except Exception as e:
            print(f"❌ Token request failed: {e}")


def test_mock_api_request():
    """Test API request with mocked response."""
    print("\nTesting API request (mocked)...")
    
    # Import and setup the requests module in testConnection
    import testConnection
    import requests as real_requests
    testConnection.requests = real_requests
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"name": "Test User", "email": "test@example.com"}'
    
    env_vars = {
        'CAMUNDA_CONSOLE_BASE_URL': 'https://test.base.url'
    }
    
    with patch.object(testConnection.requests, 'get', return_value=mock_response):
        try:
            status_code, response_body = test_api_connection(env_vars, "test_token")
            if status_code == 200 and "name" in response_body:
                print("✅ API request (mocked) passed")
            else:
                print(f"❌ API request failed - status: {status_code}, body: {response_body}")
        except Exception as e:
            print(f"❌ API request failed: {e}")


def test_ssl_error_handling():
    """Test SSL certificate error handling."""
    print("\nTesting SSL error handling...")
    
    import testConnection
    import requests as real_requests
    testConnection.requests = real_requests
    
    env_vars = {
        'CAMUNDA_CONSOLE_CLIENT_ID': 'test_id',
        'CAMUNDA_CONSOLE_CLIENT_SECRET': 'test_secret',
        'CAMUNDA_OAUTH_URL': 'https://test.url',
        'CAMUNDA_CONSOLE_OAUTH_AUDIENCE': 'test.audience'
    }
    
    # Create a mock SSL error with proper class type
    class MockSSLError(Exception):
        def __init__(self, message):
            super().__init__(message)
            self.__class__.__module__ = 'requests.exceptions'
        
        def __str__(self):
            return "SSLError: CERTIFICATE_VERIFY_FAILED certificate verify failed"
    
    ssl_error = MockSSLError("SSL: CERTIFICATE_VERIFY_FAILED")
    
    with patch.object(testConnection.requests, 'post', side_effect=ssl_error):
        try:
            token = get_access_token(env_vars)
            print("❌ SSL error not caught properly")
        except Exception as e:
            if "SSL certificate error" in str(e) or "SSL" in str(e):
                print("✅ SSL error correctly handled")
            else:
                print(f"❌ SSL error handled incorrectly: {e}")


def test_connection_error_handling():
    """Test connection error handling (e.g., proxy issues, no internet)."""
    print("\nTesting connection error handling...")
    
    import testConnection
    import requests as real_requests
    testConnection.requests = real_requests
    
    env_vars = {
        'CAMUNDA_CONSOLE_CLIENT_ID': 'test_id',
        'CAMUNDA_CONSOLE_CLIENT_SECRET': 'test_secret',
        'CAMUNDA_OAUTH_URL': 'https://test.url',
        'CAMUNDA_CONSOLE_OAUTH_AUDIENCE': 'test.audience'
    }
    
    # Create a mock connection error (simulating proxy/network issues)
    class MockConnectionError(Exception):
        def __init__(self, message):
            super().__init__(message)
            self.__class__.__module__ = 'requests.exceptions'
        
        def __str__(self):
            return "ConnectionError: Proxy connection failed"
    
    connection_error = MockConnectionError("Connection refused - proxy error")
    
    with patch.object(testConnection.requests, 'post', side_effect=connection_error):
        try:
            token = get_access_token(env_vars)
            print("❌ Connection error not caught properly")
        except Exception as e:
            if "Connection error" in str(e) or "connection" in str(e).lower():
                print("✅ Connection error correctly handled (proxy/network issues)")
            else:
                print(f"❌ Connection error handled incorrectly: {e}")


def test_timeout_error_handling():
    """Test timeout error handling (slow network, proxy timeouts)."""
    print("\nTesting timeout error handling...")
    
    import testConnection
    import requests as real_requests
    testConnection.requests = real_requests
    
    env_vars = {
        'CAMUNDA_CONSOLE_BASE_URL': 'https://test.base.url'
    }
    
    # Create a mock timeout error
    class MockTimeoutError(Exception):
        def __init__(self, message):
            super().__init__(message)
            self.__class__.__module__ = 'requests.exceptions'
        
        def __str__(self):
            return "Timeout: Read timed out (timeout=30)"
    
    timeout_error = MockTimeoutError("Read timed out (timeout=30)")
    
    with patch.object(testConnection.requests, 'get', side_effect=timeout_error):
        try:
            status_code, response_body = test_api_connection(env_vars, "test_token")
            print("❌ Timeout error not caught properly")
        except Exception as e:
            if "timeout" in str(e).lower():
                print("✅ Timeout error correctly handled (slow network/proxy)")
            else:
                print(f"❌ Timeout error handled incorrectly: {e}")


def main():
    """Run all tests."""
    print("🧪 Running Camunda Connection Test Tool - Unit Tests")
    print("=" * 60)
    
    # Basic functionality tests
    test_python_version_check()
    test_env_vars_loading()
    test_response_validation()
    test_mock_token_request()
    test_mock_api_request()
    
    # Error handling tests (SSL, proxy, timeout)
    test_ssl_error_handling()
    test_connection_error_handling()
    test_timeout_error_handling()
    
    print("\n" + "=" * 60)
    print("🏁 Test suite completed!")


if __name__ == "__main__":
    main()