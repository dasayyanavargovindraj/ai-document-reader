from google.genai import types

try:
    part1 = types.Part.from_bytes(data=b"hello", mime_type="text/plain")
    part2 = types.Part.from_text(text="world")
    print("Success creating parts:", part1, part2)
except Exception as e:
    print("Error:", e)
