import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Hello",
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful assistant."
        )
    )
    print("Response text:", response.text)
except Exception as e:
    print("Error:", e)
