import streamlit as st
import json
import tech_agent 
import news_agent  
import orchestrator  


st.set_page_config(page_title="TrendSignal AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e2227; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 TrendSignal AI: Multi-Agent Market Intelligence")
st.caption("Mumbai ML GenAI Hackathon | Project: Autonomous Multi-Agent System")

st.sidebar.header("🕹️ Agent Swarm Control")
user_ticker = st.sidebar.text_input("Enter Ticker Symbol", value="RELIANCE.NS").upper()
st.sidebar.info("Tip: Add '.NS' for Indian stocks (e.g., VEDL.NS)")

st.sidebar.divider()
st.sidebar.subheader("System Settings")
mode = st.sidebar.toggle("Safe Demo Mode", value=True)

if st.sidebar.button("🚀 RUN SYSTEM SCAN", use_container_width=True):
    col1, col2 = st.columns(2)
    
    with st.spinner(f"Agents are scouting {user_ticker}..."):
        
        tech_data = tech_agent.get_tech_analysis(user_ticker)
        context_data = news_agent.get_news_analysis(user_ticker)
        final_report = orchestrator.run_orchestrator(tech_data, context_data)
    with col1:
        st.subheader("📊 Technical Agent Sensor")
        if tech_data['signal'] != "Error":
            m1, m2 = st.columns(2)
            m1.metric("Current Price", f"₹{tech_data['price']}")
            m2.metric("Technical Signal", tech_data['signal'], delta=tech_data['signal'])
            
            st.info(f"**Metric Detail:** {tech_data['confidence']} | {tech_data['detail']}")
        else:
            st.error(f"Technical Agent Error: {tech_data['detail']}")
    with col2:
        st.subheader("📰 Context Agent Sensor")
        st.metric("Sentiment Score", context_data['score'])
        st.success(f"**Top Insight Found:**\n\n{context_data['headline']}")

    st.divider()
    st.subheader("🎯 Orchestrator Final Intelligence Report")
    with st.container(border=True):
        st.markdown(final_report)