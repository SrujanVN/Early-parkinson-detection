
import os
from google import genai
import sys

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def test_gemini():
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("Client initialized")
        
        print("Listing available models:")
        models = list(client.models.list())
        found_model = None
        for model in models:
            print(f"  - {model.name}")
            if "flash" in model.name.lower():
                found_model = model.name
        
        print("Testing all available Flash models...")
        for model in models:
            if "flash" in model.name.lower():
                try:
                    print(f"Trying {model.name}...")
                    response = client.models.generate_content(
                        model=model.name,
                        contents="Hello"
                    )
                    print(f"SUCCESS with {model.name}: {response.text[:50]}...")
                    return True
                except Exception as e:
                    print(f"FAILED with {model.name}: {e}")
        return False
    except Exception as e:
        print(f"Failed: {e}")
        return False

if __name__ == "__main__":
    test_gemini()
