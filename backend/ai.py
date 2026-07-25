import requests
import json

API_KEY ="YOUR_API_KEY_HERE"
URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "google/gemma-3-4b-it:free"


def ask_ai(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Vendor AI Project"
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(URL, headers=headers, data=json.dumps(data))

    result = response.json()

    # Debug mode
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return str(result)