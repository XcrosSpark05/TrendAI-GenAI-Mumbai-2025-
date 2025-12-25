import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import tech_agent
import news_agent
import orchestrator
# import google.generativeai as genai  # Uncomment to use Gemini

# --- 1. INITIALIZE SESSION STATE (NEW) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

st.set_page_config(page_title="TrendSignal AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* ===== TEXT INPUT (TICKER SEARCH FIX) ===== */
input[type="text"] {
    background: #020617 !important;
    color: #e5e7eb !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-size: 15px !important;
    box-shadow: inset 0 0 0 1px rgba(56,189,248,0.15);
}
input::placeholder { color: #64748b !important; }
input[type="text"]:focus {
    outline: none !important;
    border: 1px solid #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56,189,248,0.35) !important;
}
label { color: #cbd5f5 !important; font-weight: 600; }
html, body, [class*="css"]  { font-family: 'Inter', 'Segoe UI', sans-serif; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0f14, #0f141b);
    border-right: 1px solid #1f2937;
}
.stMetric {
    background: linear-gradient(145deg, #121826, #0b0f1a);
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}
button[data-baseweb="tab"] { font-size: 15px; font-weight: 600; color: #9ca3af; }
button[data-baseweb="tab"][aria-selected="true"] { color: #38bdf8; border-bottom: 3px solid #38bdf8; }
[data-testid="stExpander"] { background: #0f172a; border-radius: 12px; border: 1px solid #1f2937; }
.verdict-box {
    background: linear-gradient(135deg, #0f172a, #020617);
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #1f2937;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
}
.advisor-box {
    background: linear-gradient(135deg, #052e16, #020617);
    padding: 22px;
    border-radius: 16px;
    border-left: 6px solid #22c55e;
    margin-top: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.5);
}
/* Chat Message Bubbles */
.stChatMessage {
    background: rgba(30, 41, 59, 0.7) !important;
    border-radius: 15px !important;
    border: 1px solid #334155 !important;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.header("Agent Swarm Control")
user_ticker = st.sidebar.text_input("Enter Ticker Symbol", value="RELIANCE.NS").upper()
mode = st.sidebar.toggle("Safe Demo Mode", value=True)

# Add clear chat button
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()


def draw_candlestick(ticker):
    df, _ = tech_agent.get_stock_data(ticker)
    if df is None or df.empty:
        st.warning("⚠️ No historical data available.")
        return None
    df['SMA_50'] = df['Close'].rolling(50).mean()
    fig = go.Figure([
        go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market"),
        go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color="orange", width=1.5), name="50 SMA")
    ])
    fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=20, b=0))
    return fig


def draw_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        gauge={"axis": {"range": [-1, 1]}, "bar": {"color": "white"},
               "steps": [{"range": [-1, -0.3], "color": "#ff4b4b"}, {"range": [-0.3, 0.3], "color": "gray"}, {"range": [0.3, 1], "color": "#09ab3b"}]},
        title={"text": "Analyst Sentiment"}
    ))
    fig.update_layout(template="plotly_dark", height=260)
    return fig


def generate_human_advice(tech_data, sentiment_score):
    trend = tech_data["signal"]
    if trend == "Bullish":
        if sentiment_score > 0.3: return "📈 Strong momentum detected. Holding is reasonable. Fresh buying should be gradual."
        elif sentiment_score < 0: return "⚠️ Technicals strong but sentiment mixed. Consider partial profit booking."
        else: return "📊 Bullish structure but weak conviction. Wait for confirmation before acting."
    if trend == "Bearish": return "📉 Trend is weak. Avoid new buying and protect capital."
    if trend == "Neutral": return "⏸️ Market lacks clear direction. Best strategy is wait-and-watch."
    return "⚠️ Insufficient data. Avoid taking positions until clarity improves."


# --- MAIN APP ---
st.title("📈 TrendSignal AI: Multi-Agent Intelligence")

if st.sidebar.button("🚀 INITIATE SCAN"):
    try:
        with st.spinner("Initiating Agent Swarm..."):
            stock_info = tech_agent.get_detailed_stock_info(user_ticker)
            tech_data = tech_agent.get_tech_analysis(user_ticker)
            context_data = news_agent.get_news_analysis(user_ticker)
            final_report = orchestrator.run_orchestrator(tech_data, context_data)
            
            # Store results in session state for Chat Context
            st.session_state.last_analysis = {
                "ticker": user_ticker,
                "price": stock_info['price'],
                "tech_signal": tech_data["signal"],
                "news_score": context_data["score"],
                "summary": final_report
            }

        st.subheader(f"{user_ticker} — Market Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Price", f"{stock_info['price']} {stock_info['currency']}", f"{stock_info['change_pct']}%")
        c2.metric("Open", stock_info['open'])
        c3.metric("Day High", stock_info['day_high'])
        c4.metric("Day Low", stock_info['day_low'])

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Market Cap", f"₹ {round(stock_info['mkt_cap']/1e12,2)} T")
        c6.metric("P/E Ratio", stock_info['pe_ratio'])
        c7.metric("52W High", stock_info['high_52'])
        c8.metric("52W Low", stock_info['low_52'])

        tab1, tab2, tab3, tab4 = st.tabs(["📈 Chart", "📊 Technicals", "🧠 Intelligence", "📰 News"])
        with tab1:
            fig = draw_candlestick(user_ticker)
            if fig: st.plotly_chart(fig, use_container_width=True)
        with tab2:
            st.metric("Trend Signal", tech_data["signal"])
            st.caption(tech_data["confidence"])
            st.caption(tech_data["detail"])
        with tab3:
            st.plotly_chart(draw_gauge(context_data["score"]), use_container_width=True)
        with tab4:
            for h in context_data["headline"].split("|"):
                with st.expander(f" {h[:70]}..."): st.write(h)

        st.divider()
        st.subheader("Final Verdict")
        st.markdown(f"<div class='verdict-box'>{final_report}</div>", unsafe_allow_html=True)

        advice = generate_human_advice(tech_data, context_data["score"])
        st.subheader("🤝 What Should You Do Now?")
        st.markdown(f"<div class='advisor-box'>{advice}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error("❌ Analysis failed. Please try another ticker or later.")
        st.caption(str(e))

# --- CHATBOT SECTION (NEW) ---
st.divider()
st.subheader("💬 Swarm Intelligence Chat")

# Display historical messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("Ask about technical indicators, entry points, or risks..."):
    # 1. Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Logic to generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Consulting swarm agents..."):
            # Context Preparation
            context = ""
            if st.session_state.last_analysis:
                data = st.session_state.last_analysis
                context = f"Context: Ticker {data['ticker']}, Price {data['price']}, Signal {data['tech_signal']}, Sentiment {data['news_score']}. Summary: {data['summary']}"
            
            # --- API CALL PLACEHOLDER ---
            # Replace the lines below with your actual LLM call (e.g., openai.ChatCompletion or genai.GenerativeModel)
            ai_response = f"I see you're asking about {user_ticker}. "
            if st.session_state.last_analysis:
                ai_response += f"Based on the scan, the current signal is {st.session_state.last_analysis['tech_signal']}. "
            ai_response += f"Your query was: '{prompt}'. I recommend looking at the 50 SMA support levels shown in the chart above."
            # -----------------------------
            
            st.markdown(ai_response)
    
    # 3. Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": ai_response})