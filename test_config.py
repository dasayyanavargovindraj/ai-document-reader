import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

try:
    config = types.GenerateContentConfig(
        system_instruction="You are a helpful assistant."
    )
    print("Config created successfully:", config)
except Exception as e:
    print("Error:", e)
