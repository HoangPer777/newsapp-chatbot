import google.generativeai as genai
import os

# Try getting key from env vars (standard way in docker)
api_key = os.environ.get("GOOGLE_API_KEY")

# Fallback: try reading from .env manually
if not api_key:
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.strip().split("=", 1)[1]
                    break
    except:
        pass

output_lines = []
if not api_key:
    output_lines.append("ERROR: GOOGLE_API_KEY not found.")
else:
    output_lines.append(f"Using API Key: {api_key[:5]}...{api_key[-5:]}")
    genai.configure(api_key=api_key)
    output_lines.append("Listing models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                output_lines.append(f"- {m.name}")
    except Exception as e:
        output_lines.append(f"CRASH: {e}")

# Write to file (so we can read it from host via volume mount)
with open("models_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("Done writing to models_output.txt")
