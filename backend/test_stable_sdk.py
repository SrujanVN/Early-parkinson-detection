import google.generativeai as genai
import os

api_key = "AIzaSyAy3JIcXbmjkVB0DR22qGnS9Cn9wmLZzhQ"

try:
    print(f"Configuring with key: {api_key[:10]}...")
    genai.configure(api_key=api_key)
    
    print("Listing models...")
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Available model: {m.name}")
            available_models.append(m.name)
    
    if available_models:
        model_name = available_models[0]
        print(f"Testing with: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hi!")
        print(f"Response: {response.text}")
    else:
        print("No generation models found.")

except Exception as e:
    print(f"Error: {e}")
