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

try:
    response = requests.post(URL, headers=headers, data=json.dumps(payload))
except Exception as e:
    return f"System Error: {str(e)}"
import os
import requests
import json
from dotenv import load_dotenv
import tech_agent
import news_agent

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={API_KEY}"

def run_orchestrator(tech_data, context_data):
    print("🧠 Orchestrator: Synthesizing data with Gemini 3.0...")
    
    prompt_text = f"""
    You are a Senior Multi-Agent Market Strategist. 
    Analyze the following data from your specialized agents and provide a high-impact summary.
    
    TECHNICAL DATA: {tech_data}
    NEWS CONTEXT: {context_data}
    
    Output Format:
    - SUMMARY: (2 sentences max)
    - CONFLICT ALERT: (Mention if news contradicts technicals)
    - FINAL SIGNAL: [Bullish/Bearish/Neutral]
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and result['candidates'][0]['content']['parts']:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "⚠️ AI Response was empty or blocked by safety filters."
        else:
            return f"❌ API Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ System Error: {str(e)}"

if __name__ == "__main__":
    user_ticker = input("Enter Stock Ticker (e.g., RELIANCE, VEDL, TSLA): ")
    
    try:
        live_tech = tech_agent.get_tech_analysis(user_ticker)
        live_news = news_agent.get_news_analysis(user_ticker)
        
        final_report = run_orchestrator(live_tech, live_news)
        
        print("\n" + "="*50)
        print(f"🚀 FINAL INTELLIGENCE REPORT: {user_ticker}")
        print("="*50)
        print(final_report)
    except Exception as e:
        print(f"❌ Error during dynamic fetch: {e}")