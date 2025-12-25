import streamlit as st
import pandas as pd
import tech_agent
import news_agent
import orchestrator
import google.generativeai as genai
import os
from dotenv import load_dotenv
from lightweight_charts_v5 import lightweight_charts_v5_component
import plotly.graph_objects as go

# --- 1. INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None

# --- 2. CONFIGURE GEMINI SECURELY ---
load_dotenv() 
try:
    LATEST_MODEL = "gemini-3-flash-preview" 
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        st.error("Missing API Key! Please check your .env file.")
        st.stop()
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

SYSTEM_PROMPT = """
You are 'TrendAI', a senior stock broker and market analyst. 
Your tone is professional, authoritative, and data-driven.

STRICT OPERATING RULES:
1. TOPIC FILTER: You only discuss stock market analysis, technicals, news, and trading strategy.
2. If a user asks a question NOT related to stocks, respond exactly with: 
   "I am not a general purpose chat bot. I am designed only to address your query related to stocks."
3. Always reference the specific ticker data provided in the context.
4. Include a disclaimer that you are an AI assistant and not a licensed financial advisor.
"""

# --- 3. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="TrendSignal AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #020617; }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #0f172a, #020617);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    .verdict-box {
        background: #0f172a;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #1e293b;
        border-left: 6px solid #38bdf8;
    }
    .stChatMessage { background: #0f172a !important; border-radius: 10px !important; border: 1px solid #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
st.sidebar.header("Agent Swarm Control")
user_ticker = st.sidebar.text_input("Enter Ticker Symbol", value="RELIANCE.NS").upper()

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# --- 5. LIGHTWEIGHT CHART UTILITY ---
def render_lightweight_chart():
    data = st.session_state.chart_data
    if not data:
        return
    
    # Static key using the ticker ensures the chart doesn't unmount during chat
    lightweight_charts_v5_component(
        name="MarketChart",
        key=f"chart_{st.session_state.last_analysis['ticker']}",
        charts=[{
            "chart": {
                "layout": {"background": {"color": "#020617"}, "textColor": "#f1f5f9"},
                "grid": {"vertLines": {"visible": False}, "horzLines": {"color": "#1e293b"}},
            },
            "series": [
                {
                    "type": "Candlestick",
                    "data": data['ohlc'],
                    "options": {"upColor": "#22c55e", "downColor": "#ef4444"}
                },
                {
                    "type": "Line",
                    "data": data['sma'],
                    "options": {"color": "#f97316", "lineWidth": 2, "title": "50 SMA"}
                }
            ],
            "height": 500
        }],
        height=550
    )

def draw_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        gauge={"axis": {"range": [-1, 1], "tickcolor": "white"}, "bar": {"color": "white"},
               "steps": [{"range": [-1, -0.3], "color": "#ef4444"}, {"range": [0.3, 1], "color": "#22c55e"}]},
        title={"text": "Analyst Sentiment", "font": {"size": 20}}
    ))
    fig.update_layout(template="plotly_dark", height=260, paper_bgcolor="rgba(0,0,0,0)")
    return fig

# --- 6. MAIN APP INTERFACE ---
st.title("📈 TrendSignal AI: Multi-Agent Intelligence")

# SCAN TRIGGER
if st.sidebar.button("🚀 INITIATE SCAN"):
    try:
        with st.spinner("Processing swarm signals..."):
            # Fetch data
            stock_info = tech_agent.get_detailed_stock_info(user_ticker)
            tech_data = tech_agent.get_tech_analysis(user_ticker)
            context_data = news_agent.get_news_analysis(user_ticker)
            final_report = orchestrator.run_orchestrator(tech_data, context_data)
            
            # Prepare chart data for session state
            df, _ = tech_agent.get_stock_data(user_ticker)
            df = df.reset_index()
            ohlc = df.apply(lambda row: {"time": str(row['Date'].date()), "open": float(row['Open']), "high": float(row['High']), "low": float(row['Low']), "close": float(row['Close'])}, axis=1).tolist()
            df['SMA_50'] = df['Close'].rolling(50).mean()
            sma = df.dropna(subset=['SMA_50']).apply(lambda row: {"time": str(row['Date'].date()), "value": float(row['SMA_50'])}, axis=1).tolist()
            
            # Save to Session State
            st.session_state.chart_data = {"ohlc": ohlc, "sma": sma}
            st.session_state.last_analysis = {
                "ticker": user_ticker, 
                "info": stock_info,
                "tech": tech_data,
                "news": context_data,
                "summary": final_report
            }
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")

# PERSISTENT DISPLAY (Outside the button block)
if st.session_state.last_analysis:
    analysis = st.session_state.last_analysis
    stock_info = analysis['info']
    
    st.subheader(f"{analysis['ticker']} — Market Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Price", f"{stock_info['price']} {stock_info['currency']}", f"{stock_info['change_pct']}%")
    c2.metric("Market Open", stock_info['open'])
    c3.metric("Day Range (High)", stock_info['day_high'])
    c4.metric("Day Range (Low)", stock_info['day_low'])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Market Cap", f"₹ {round(stock_info['mkt_cap']/1e12,2)} T")
    c6.metric("P/E Ratio", round(stock_info['pe_ratio'], 2) if isinstance(stock_info['pe_ratio'], (int, float)) else "N/A")
    c7.metric("52-Week High", stock_info['high_52'])
    c8.metric("52-Week Low", stock_info['low_52'])

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Price Chart", "📊 Technical Swarm", "🧠 Intelligence Score", "📰 News"])
    with tab1:
        render_lightweight_chart()
    with tab2:
        st.write(f"### Current Trend: **{analysis['tech']['signal']}**")
        st.info(analysis['tech']["detail"])
    with tab3:
        st.plotly_chart(draw_gauge(analysis['news']["score"]), use_container_width=True)
    with tab4:
        for h in analysis['news']["headline"].split("|"):
            if h.strip():
                with st.expander(f" 📰 {h[:80]}..."): st.write(h)

    st.divider()
    st.subheader("Final Verdict")
    st.markdown(f"<div class='verdict-box'>{analysis['summary']}</div>", unsafe_allow_html=True)

# --- 7. CHATBOT INTERFACE ---
st.divider()
st.subheader("💬 TrendAI - Terminal Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask TrendAI about this ticker..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing signals..."):
            data_context = "No live scan performed."
            if st.session_state.last_analysis:
                d = st.session_state.last_analysis
                data_context = f"Ticker: {d['ticker']}, Price: {d['info']['price']}, Signal: {d['tech']['signal']}, Summary: {d['summary']}"

            model = genai.GenerativeModel(model_name=LATEST_MODEL, system_instruction=SYSTEM_PROMPT)
            ai_response = model.generate_content(f"DATA: {data_context}\n\nUSER: {prompt}").text
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})