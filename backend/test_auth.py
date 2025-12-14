"""
Test script for authentication endpoints
Run this after starting the Flask server to test authentication
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_register():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    url = f"{BASE_URL}/api/register"
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "test123456",
        "role": "Patient"
    }
    
    response = requests.post(url, json=test_user)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201

def test_register_duplicate():
    """Test duplicate registration"""
    print("\n=== Testing Duplicate Registration ===")
    url = f"{BASE_URL}/api/register"
    
    test_user = {
        "email": "test@example.com",
        "password": "test123456",
        "role": "Patient"
    }
    
    response = requests.post(url, json=test_user)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 409

def test_login():
    """Test user login"""
    print("\n=== Testing Login ===")
    url = f"{BASE_URL}/api/login"
    
    login_data = {
        "email": "test@example.com",
        "password": "test123456"
    }
    
    session = requests.Session()
    response = session.post(url, json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        # Test protected endpoint
        print("\n=== Testing Protected Endpoint (/api/me) ===")
        me_response = session.get(f"{BASE_URL}/api/me")
        print(f"Status Code: {me_response.status_code}")
        print(f"Response: {json.dumps(me_response.json(), indent=2)}")
        return me_response.status_code == 200
    
    return False

def test_login_invalid():
    """Test invalid login"""
    print("\n=== Testing Invalid Login ===")
    url = f"{BASE_URL}/api/login"
    
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(url, json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 401

def test_logout():
    """Test logout"""
    print("\n=== Testing Logout ===")
    url = f"{BASE_URL}/api/logout"
    
    session = requests.Session()
    # First login
    login_data = {
        "email": "test@example.com",
        "password": "test123456"
    }
    session.post(f"{BASE_URL}/api/login", json=login_data)
    
    # Then logout
    response = session.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Try to access protected endpoint after logout
    me_response = session.get(f"{BASE_URL}/api/me")
    print(f"\nProtected endpoint after logout - Status Code: {me_response.status_code}")
    return me_response.status_code == 401

if __name__ == "__main__":
    print("Starting Authentication Tests...")
    print("=" * 50)
    
    try:
        # Run tests
        test_register()
        test_register_duplicate()
        test_login()
        test_login_invalid()
        test_logout()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server.")
        print("Make sure the Flask server is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"\nERROR: {e}")
