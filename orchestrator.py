import os
import requests
import json
from dotenv import load_dotenv
import tech_agent
import news_agent

# 1. INITIALIZE
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
            # Safety Check: Ensure the AI actually returned a candidate
            if 'candidates' in result and result['candidates'][0]['content']['parts']:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "⚠️ AI Response was empty or blocked by safety filters."
        else:
            return f"❌ API Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ System Error: {str(e)}"

# 2. EXECUTION BLOCK (This is what was missing)
if __name__ == "__main__":
    # Ask once
    user_ticker = input("Enter Stock Ticker (e.g., RELIANCE, VEDL, TSLA): ")
    
    try:
        # Pass the same ticker to BOTH specialized agents
        live_tech = tech_agent.get_tech_analysis(user_ticker)
        live_news = news_agent.get_news_analysis(user_ticker)
        
        # The Brain synthesizes both
        final_report = run_orchestrator(live_tech, live_news)
        
        print("\n" + "="*50)
        print(f"🚀 FINAL INTELLIGENCE REPORT: {user_ticker}")
        print("="*50)
        print(final_report)
    except Exception as e:
        print(f"❌ Error during dynamic fetch: {e}")