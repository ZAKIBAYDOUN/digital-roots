#!/usr/bin/env python3
import streamlit as st
import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Add agents to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all agents
from agents.ghc_dt import run_ghc_dt
from agents.strategy import run_strategy
from agents.finance import run_finance
from agents.operations import run_operations
from agents.market import run_market
from agents.compliance import run_compliance
from agents.code import run_code
from agents.innovation import run_innovation
from agents.risk import run_risk

# Configuration
LANGGRAPH_API_URL = "https://ground-control-a0ae430fa0b85ca09ebb486704b69f2b.us.langgraph.app"

# Language configuration
LANGUAGES = {
    "en": "🇺🇸 English",
    "es": "🇪🇸 Español", 
    "is": "🇮🇸 Íslenska",
    "fr": "🇫🇷 Français"
}

# Available agents
AGENTS = {
    "ghc_dt": {"name": "CEO Digital Twin", "icon": "👨‍💼", "func": run_ghc_dt},
    "strategy": {"name": "Strategy Agent", "icon": "🎯", "func": run_strategy},
    "finance": {"name": "Finance Agent", "icon": "💰", "func": run_finance},
    "operations": {"name": "Operations Agent", "icon": "⚙️", "func": run_operations},
    "market": {"name": "Market Agent", "icon": "📈", "func": run_market},
    "compliance": {"name": "Compliance Agent", "icon": "⚖️", "func": run_compliance},
    "code": {"name": "Code Agent", "icon": "💻", "func": run_code},
    "innovation": {"name": "Innovation Agent", "icon": "💡", "func": run_innovation},
    "risk": {"name": "Risk Agent", "icon": "🛡️", "func": run_risk}
}

def init_session_state():
    """Initialize session state variables"""
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'evidence_log' not in st.session_state:
        st.session_state.evidence_log = []

def get_text(key, language='en'):
    """Get text in specified language"""
    texts = {
        'title': {
            'en': '🌱 Digital Roots - CEO Digital Twin',
            'es': '🌱 Digital Roots - CEO Digital Twin',
            'is': '🌱 Digital Roots - CEO Digital Twin', 
            'fr': '🌱 Digital Roots - CEO Digital Twin'
        },
        'chat_tab': {
            'en': 'Chat',
            'es': 'Chat',
            'is': 'Spjall',
            'fr': 'Discussion'
        },
        'ingest_tab': {
            'en': 'Ingest',
            'es': 'Ingerir',
            'is': 'Inntaka',
            'fr': 'Ingérer'
        },
        'evidence_tab': {
            'en': 'Evidence',
            'es': 'Evidencia',
            'is': 'Sönnun',
            'fr': 'Preuves'
        },
        'governance_tab': {
            'en': 'Governance',
            'es': 'Gobernanza',
            'is': 'Stjórnun',
            'fr': 'Gouvernance'
        }
    }
    return texts.get(key, {}).get(language, texts.get(key, {}).get('en', key))

def chat_interface():
    """Main chat interface"""
    st.header("💬 CEO Digital Twin Chat")
    
    # Agent selection
    selected_agent = st.selectbox(
        "Select Agent:",
        options=list(AGENTS.keys()),
        format_func=lambda x: f"{AGENTS[x]['icon']} {AGENTS[x]['name']}"
    )
    
    # Question input
    question = st.text_area("Ask your question:", height=100)
    
    if st.button("Send") and question:
        with st.spinner("Processing..."):
            try:
                # Call the selected agent
                agent_func = AGENTS[selected_agent]["func"]
                result = agent_func(question)
                
                # Add to chat history
                chat_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "agent": selected_agent,
                    "question": question,
                    "answer": result["answer"],
                    "tokens": result["meta"]["tokens"]
                }
                st.session_state.chat_history.append(chat_entry)
                st.session_state.evidence_log.append(chat_entry)
                
                # Display result
                st.success(f"**{AGENTS[selected_agent]['name']}** ({result['meta']['tokens']} tokens)")
                st.write(result["answer"])
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Chat history
    if st.session_state.chat_history:
        st.subheader("Recent Conversations")
        for entry in reversed(st.session_state.chat_history[-5:]):
            with st.expander(f"{AGENTS[entry['agent']]['icon']} {entry['question'][:50]}..."):
                st.write(f"**Agent:** {AGENTS[entry['agent']]['name']}")
                st.write(f"**Question:** {entry['question']}")
                st.write(f"**Answer:** {entry['answer']}")
                st.write(f"**Tokens:** {entry['tokens']}")

def ingest_interface():
    """Data ingestion interface"""
    st.header("📥 Data Ingest")
    
    st.info("Upload and process data for the CEO Digital Twin system")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'csv', 'json'])
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Process file (placeholder)
        if st.button("Process File"):
            with st.spinner("Processing file..."):
                # Simulate processing
                st.success("File processed successfully!")
                
    # URL ingestion
    st.subheader("URL Ingestion")
    url = st.text_input("Enter URL to process:")
    
    if st.button("Process URL") and url:
        with st.spinner("Processing URL..."):
            try:
                # Simulate URL processing
                st.success(f"URL processed: {url}")
            except Exception as e:
                st.error(f"Error processing URL: {str(e)}")

def evidence_interface():
    """Evidence and audit log interface"""
    st.header("📋 Evidence Log")
    
    if st.session_state.evidence_log:
        st.info(f"Total interactions: {len(st.session_state.evidence_log)}")
        
        # Display evidence log
        for i, entry in enumerate(reversed(st.session_state.evidence_log)):
            with st.expander(f"Entry {len(st.session_state.evidence_log)-i}: {entry['timestamp'][:19]}"):
                st.json(entry)
                
        # Export functionality
        if st.button("Export Evidence Log"):
            evidence_json = json.dumps(st.session_state.evidence_log, indent=2)
            st.download_button(
                label="Download Evidence Log",
                data=evidence_json,
                file_name=f"evidence_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.info("No evidence logged yet. Start chatting to generate evidence.")

def governance_interface():
    """Governance and configuration interface"""
    st.header("⚖️ Governance")
    
    # System configuration
    st.subheader("System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**API Configuration**")
        st.code(f"LangGraph URL: {LANGGRAPH_API_URL}")
        st.write("**Available Agents**")
        for agent_id, agent_info in AGENTS.items():
            st.write(f"- {agent_info['icon']} {agent_info['name']}")
    
    with col2:
        st.write("**System Status**")
        # Check system health
        for agent_id, agent_info in AGENTS.items():
            try:
                # Test agent with simple query
                result = agent_info["func"]("System status check")
                if "OPENAI_API_KEY not configured" in result["answer"]:
                    status = "⚠️ API Key Missing"
                elif result["answer"].startswith("Error:"):
                    status = "❌ Error"
                else:
                    status = "✅ Working"
            except:
                status = "❌ Error"
            st.write(f"- {agent_info['name']}: {status}")
    
    # Compliance information
    st.subheader("Compliance & Security")
    st.info("""
    - All interactions are logged for audit purposes
    - Data is processed securely using OpenAI API
    - Evidence log available for compliance review
    - Multi-language support enabled
    """)

def main():
    """Main application"""
    # Page configuration
    st.set_page_config(
        page_title="Digital Roots - CEO Digital Twin",
        page_icon="🌱",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🌱 Digital Roots")
        st.write("**CEO Digital Twin Platform**")
        
        # Language selector
        language = st.selectbox(
            "Language:",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.language)
        )
        st.session_state.language = language
        
        # Agent status
        st.subheader("🤖 Agents Status")
        for agent_id, agent_info in AGENTS.items():
            st.write(f"{agent_info['icon']} {agent_info['name']}")
    
    # Main title
    st.title(get_text('title', st.session_state.language))
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        get_text('chat_tab', st.session_state.language),
        get_text('ingest_tab', st.session_state.language),
        get_text('evidence_tab', st.session_state.language),
        get_text('governance_tab', st.session_state.language)
    ])
    
    with tab1:
        chat_interface()
    
    with tab2:
        ingest_interface()
    
    with tab3:
        evidence_interface()
    
    with tab4:
        governance_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("🌱 **Digital Roots** - Cannabis cultivation management platform | Built for ZAKIBAYDOUN")

if __name__ == "__main__":
    main()