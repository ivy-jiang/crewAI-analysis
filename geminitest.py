import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ Error: Could not find GEMINI_API_KEY")
else:
    client = genai.Client()
    print("Listing available models...")
    try:
        print("Searching for Flash/Pro models...")
        found = False
        for m in client.models.list():
            if 'flash' in m.name.lower() or 'pro' in m.name.lower():
                print(f" - {m.name}")
                found = True
        if not found:
            print("No 'flash' or 'pro' models found.")
            
    except Exception as e:
        print(f"Error listing models: {e}")