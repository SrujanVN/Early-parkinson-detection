import os
from google import genai

# Use the provided API key
api_key = "AIzaSyAy3JIcXbmjkVB0DR22qGnS9Cn9wmLZzhQ"

try:
    print(f"Attempting to connect with key: {api_key[:10]}...")
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Say 'Connection successful' if you can hear me."
    )
    
    print("-" * 20)
    print("RESPONSE:")
    print(response.text)
    print("-" * 20)
    print("✅ Connection test passed!")

except Exception as e:
    print("-" * 20)
    print(f"❌ Connection test failed: {e}")
    print("-" * 20)
