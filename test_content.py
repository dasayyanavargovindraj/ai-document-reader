from google.genai import types

try:
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text="hello")]
    )
    print("Content created successfully:", content)
except Exception as e:
    print("Error:", e)
