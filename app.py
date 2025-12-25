import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import tech_agent
import news_agent
import orchestrator
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

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

# --- 3. PAGE CONFIG & ENHANCED STYLING ---
st.set_page_config(page_title="TrendSignal AI", layout="wide", initial_sidebar_state="expanded")

# Unified professional CSS for cards, buttons, and metrics
st.markdown("""
<style>
    /* Global Background and Text */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #020617; }

    /* Metric Card Styling: Dark glass effect */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #0f172a, #020617);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-3px); border-color: #38bdf8; }

    /* Fix Sidebar Styling */
    section[data-testid="stSidebar"] { background: #0b0f14; border-right: 1px solid #1e2937; }
    
    /* Input Fixes */
    input[type="text"] { background: #0f172a !important; color: #f1f5f9 !important; border: 1px solid #334155 !important; border-radius: 8px !important; }

    /* Result Boxes */
    .verdict-box {
        background: #0f172a;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #1e293b;
        border-left: 6px solid #38bdf8;
        color: #e2e8f0;
        margin-top: 15px;
    }
    .advisor-box {
        background: rgba(34, 197, 94, 0.05);
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #22c55e;
        color: #f0fdf4;
        margin-top: 20px;
    }

    /* Tab and Chat Interface styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #38bdf8; border-bottom: 2px solid #38bdf8; }
    .stChatMessage { background: #0f172a !important; border-radius: 10px !important; border: 1px solid #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
st.sidebar.header("Agent Swarm Control")
user_ticker = st.sidebar.text_input("Enter Ticker Symbol", value="RELIANCE.NS").upper()
mode = st.sidebar.toggle("Safe Demo Mode", value=True)

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# --- 5. UTILITY FUNCTIONS ---
def draw_candlestick(ticker):
    df, _ = tech_agent.get_stock_data(ticker)
    if df is None or df.empty: return None
    df['SMA_50'] = df['Close'].rolling(50).mean()
    fig = go.Figure([
        go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market"),
        go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color="#f97316", width=2), name="50 SMA")
    ])
    fig.update_layout(template="plotly_dark", height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=20, b=0))
    return fig

def draw_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        gauge={"axis": {"range": [-1, 1], "tickcolor": "white"}, "bar": {"color": "white"},
               "steps": [{"range": [-1, -0.3], "color": "#ef4444"}, {"range": [-0.3, 0.3], "color": "#475569"}, {"range": [0.3, 1], "color": "#22c55e"}]},
        title={"text": "Analyst Sentiment", "font": {"size": 20}}
    ))
    fig.update_layout(template="plotly_dark", height=260, paper_bgcolor="rgba(0,0,0,0)")
    return fig

# --- 6. MAIN APP INTERFACE ---
st.title("📈 TrendSignal AI: Multi-Agent Intelligence")

if st.sidebar.button("🚀 INITIATE SCAN"):
    try:
        with st.spinner("Initiating Swarm Intelligence..."):
            stock_info = tech_agent.get_detailed_stock_info(user_ticker)
            tech_data = tech_agent.get_tech_analysis(user_ticker)
            context_data = news_agent.get_news_analysis(user_ticker)
            final_report = orchestrator.run_orchestrator(tech_data, context_data)
            
            st.session_state.last_analysis = {
                "ticker": user_ticker, "price": stock_info['price'], 
                "pe": stock_info['pe_ratio'], "tech_signal": tech_data["signal"],
                "news_score": context_data["score"], "summary": final_report
            }

        st.subheader(f"{user_ticker} — Market Summary")
        
        # Two-row grid layout for metrics
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

        # Data Deep Dives
        tab1, tab2, tab3, tab4 = st.tabs(["📉 Price Chart", "📊 Technical Swarm", "🧠 Intelligence Score", "📰 Contextual News"])
        with tab1:
            fig = draw_candlestick(user_ticker)
            if fig: st.plotly_chart(fig, use_container_width=True)
        with tab2:
            st.write(f"### Current Trend: **{tech_data['signal']}**")
            st.info(tech_data["detail"])
        with tab3:
            st.plotly_chart(draw_gauge(context_data["score"]), use_container_width=True)
        with tab4:
            for h in context_data["headline"].split("|"):
                if h.strip():
                    with st.expander(f" 📰 {h[:80]}..."): st.write(h)

        st.divider()
        st.subheader("Final Verdict")
        st.markdown(f"<div class='verdict-box'>{final_report}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Swarm Analysis failed: {e}")

# --- 7. CHATBOT INTERFACE ---
st.divider()
st.subheader("💬 TrendAI - Terminal Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask TrendAI about the current market position..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Processing swarm signals..."):
            data_context = "No live scan performed."
            if st.session_state.last_analysis:
                d = st.session_state.last_analysis
                data_context = f"Ticker: {d['ticker']}, Price: {d['price']}, Signal: {d['tech_signal']}, Summary: {d['summary']}"

            try:
                model = genai.GenerativeModel(model_name=LATEST_MODEL, system_instruction=SYSTEM_PROMPT)
                response = model.generate_content(f"DATA CONTEXT: {data_context}\n\nUSER REQUEST: {prompt}")
                ai_response = response.text
            except Exception as e:
                ai_response = f"System Error: {str(e)}"
            
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})