import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

try:
    for m in client.models.list():
        print(repr(m))
        break
except Exception as e:
    print(f"Error: {e}")
