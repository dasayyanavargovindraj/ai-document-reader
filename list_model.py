import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    models = [m.name for m in client.models.list() if m.supported_actions and 'generateContent' in m.supported_actions]
    for m in models:
        print(m)
except Exception as e:
    print(f"Error listing models: {e}")
