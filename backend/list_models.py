from google import genai

api_key = "AIzaSyAy3JIcXbmjkVB0DR22qGnS9Cn9wmLZzhQ"

try:
    client = genai.Client(api_key=api_key)
    print("Listing models...")
    for model in client.models.list():
        print(f"Name: {model.name}")
        # Try to find supported methods or other identifiers
        attrs = [attr for attr in dir(model) if not attr.startswith('_')]
        print(f"Attributes: {attrs}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
