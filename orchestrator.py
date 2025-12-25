import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={API_KEY}"

def run_orchestrator(tech_data, context_data):
    print("🧠 Orchestrator started")
    print("Technical Data:", tech_data)
    print("Context Data:", context_data)

def run_orchestrator(tech_data, context_data):
    print("🧠 Orchestrator: Preparing AI prompt")

    prompt_text = f"""
    You are a Senior Multi-Agent Market Strategist.
    Analyze the following inputs and generate a concise market signal.

    TECHNICAL DATA: {tech_data}
    NEWS CONTEXT: {context_data}
    """

    return prompt_text


payload = {
    "contents": [{
        "parts": [{"text": prompt_text}]
    }]
}

headers = {'Content-Type': 'application/json'}
response = requests.post(URL, headers=headers, data=json.dumps(payload))
return response.text

if response.status_code == 200:
    result = response.json()
    if 'candidates' in result:
        return result['candidates'][0]['content']['parts'][0]['text']
    return "AI returned no valid response"
