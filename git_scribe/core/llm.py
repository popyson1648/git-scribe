import requests
import json

def clean_llm_output(text: str) -> str:
    """Removes markdown fencing and leading/trailing whitespace."""
    return text.strip().replace("```markdown", "").replace("```", "").strip()

def generate_text(api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Generates text using the Gemini API with a system and user prompt."""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": user_prompt}
                ]
            }
        ]
    }

    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    
    return clean_llm_output(response.json()["candidates"][0]["content"]["parts"][0]["text"])
