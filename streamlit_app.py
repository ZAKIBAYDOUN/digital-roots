"""
Green Hill Executive Cockpit - Multi-language Streamlit UI
Single entry point for Streamlit Cloud deployment
"""

import streamlit as st
import os
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional

# --- Page Configuration ---
st.set_page_config(
    page_title="Green Hill Cockpit",
    page_icon="🌿",
    layout="wide"
)

# --- Constants and Configuration ---
AGENTS = {
    "ghc_dt": "CEO Digital Twin",
    "strategy": "Strategy Advisor", 
    "finance": "Finance Advisor",
    "operations": "Operations Advisor",
    "market": "Market Advisor",
    "risk": "Risk Advisor",
    "compliance": "Compliance Advisor",
    "innovation": "Innovation Advisor",
    "code": "Code Assistant"
}

COMMANDS = {
    "analyze": "Analyze current situation",
    "recommend": "Get recommendations",
    "forecast": "Generate forecasts",
    "report": "Generate report",
    "simulate": "Run simulation",
    "optimize": "Optimize strategy"
}

LANG = {
    "en": {
        "title": "Green Hill Cockpit",
        "subtitle": "Executive intelligence for Green Hill Canarias",
        "tabs": ["💬 Chat", "📥 Ingest", "📚 Evidence", "🏛️ Governance", "🔍 Diagnostics", "🧑‍💻 Code"],
        "select_agent": "Select agent",
        "ask": "Your question",
        "send": "Send",
        "consult_all": "Consult All Agents",
        "ingest_title": "Ingest Knowledge (per agent & global)",
        "upload_files": "Upload files",
        "paste_text": "Paste text",
        "add_url": "Add URL",
        "ingest_btn": "Ingest",
        "evidence_title": "Evidence Log",
        "governance_title": "Governance State",
        "diagnostics_title": "Diagnostics",
        "test_langgraph": "Test LangGraph",
        "test_openai": "Test OpenAI",
        "code_title": "Code Agent",
        "shareholder_intro": "Welcome — this cockpit showcases our agents and executive workflows.",
        "select_language": "Select Language",
        "phase": "Phase",
        "zec_rate": "ZEC Tax Rate",
        "cash_buffer": "Cash Buffer Target"
    },
    "es": {
        "title": "Cockpit de Green Hill",
        "subtitle": "Inteligencia ejecutiva para Green Hill Canarias",
        "tabs": ["💬 Chat", "📥 Ingesta", "📚 Evidencia", "🏛️ Gobernanza", "🔍 Diagnóstico", "🧑‍💻 Código"],
        "select_agent": "Selecciona agente",
        "ask": "Tu pregunta",
        "send": "Enviar",
        "consult_all": "Consultar a Todos",
        "ingest_title": "Ingesta de Conocimiento (por agente y global)",
        "upload_files": "Subir archivos",
        "paste_text": "Pegar texto",
        "add_url": "Añadir URL",
        "ingest_btn": "Ingerir",
        "evidence_title": "Registro de Evidencia",
        "governance_title": "Estado de Gobernanza",
        "diagnostics_title": "Diagnósticos",
        "test_langgraph": "Probar LangGraph",
        "test_openai": "Probar OpenAI",
        "code_title": "Agente de Código",
        "shareholder_intro": "Bienvenidos — este cockpit presenta nuestros agentes y flujos ejecutivos.",
        "select_language": "Seleccionar Idioma",
        "phase": "Fase",
        "zec_rate": "Tasa ZEC",
        "cash_buffer": "Objetivo Buffer Efectivo"
    },
    "is": {
        "title": "Green Hill stjórnborð",
        "subtitle": "Framkvæmdagreind fyrir Green Hill Canarias",
        "tabs": ["💬 Spjall", "📥 Inntaka", "📚 Sannanir", "🏛️ Stjórnsýsla", "🔍 Greining", "🧑‍💻 Kóði"],
        "select_agent": "Veldu umboðsmann",
        "ask": "Spurning þín",
        "send": "Senda",
        "consult_all": "Ráðfæra við alla",
        "ingest_title": "Þekkingarinntaka (eftir umboðsmanni og alþjóðleg)",
        "upload_files": "Hlaða upp skjölum",
        "paste_text": "Líma texta",
        "add_url": "Bæta við veffangi",
        "ingest_btn": "Inntaka",
        "evidence_title": "Sönnunarskrá",
        "governance_title": "Stjórnsýslustaða",
        "diagnostics_title": "Greining",
        "test_langgraph": "Prófa LangGraph",
        "test_openai": "Prófa OpenAI",
        "code_title": "Kóða-umboðsmaður",
        "shareholder_intro": "Velkomin — þetta stjórnborð sýnir umboðsmennina okkar og stjórnunarferli.",
        "select_language": "Velja Tungumál",
        "phase": "Áfangi",
        "zec_rate": "ZEC Skatthlutfall",
        "cash_buffer": "Reiðufé Markmið"
    },
    "fr": {
        "title": "Cockpit Green Hill",
        "subtitle": "Intelligence exécutive pour Green Hill Canarias",
        "tabs": ["�� Chat", "📥 Ingestion", "📚 Évidence", "🏛️ Gouvernance", "🔍 Diagnostics", "🧑‍💻 Code"],
        "select_agent": "Sélectionner un agent",
        "ask": "Votre question",
        "send": "Envoyer",
        "consult_all": "Consulter tous",
        "ingest_title": "Ingestion de Connaissances (par agent & globale)",
        "upload_files": "Téléverser des fichiers",
        "paste_text": "Coller du texte",
        "add_url": "Ajouter une URL",
        "ingest_btn": "Ingestion",
        "evidence_title": "Journal d'Évidence",
        "governance_title": "État de Gouvernance",
        "diagnostics_title": "Diagnostics",
        "test_langgraph": "Tester LangGraph",
        "test_openai": "Tester OpenAI",
        "code_title": "Agent Code",
        "shareholder_intro": "Bienvenue — ce cockpit présente nos agents et flux exécutifs.",
        "select_language": "Choisir la Langue",
        "phase": "Phase",
        "zec_rate": "Taux ZEC",
        "cash_buffer": "Objectif Trésorerie"
    }
}

# File names
STATE_FILE = "state.json"
EVIDENCE_FILE = "evidence.jsonl"

# --- Environment and State Management ---
def setup_environment():
    """Bridge Streamlit secrets to environment variables for deployment."""
    secret_keys = [
        "LANGGRAPH_API_URL", "LANGGRAPH_API_KEY", "OPENAI_API_KEY",
        "DEMO_MODE", "GHC_DT_MODEL", "GHC_DT_TEMPERATURE", "GHC_DT_EVIDENCE_LOG"
    ]
    
    for key in secret_keys:
        if hasattr(st, 'secrets') and key in st.secrets:
            os.environ[key] = st.secrets[key]

# Initialize environment
setup_environment()

# API Configuration from environment variables
LANGGRAPH_API_URL = os.getenv("LANGGRAPH_API_URL", "https://ground-control-a0ae430fa0b85ca09ebb486704b69f2b.us.langgraph.app")
LANGGRAPH_API_KEY = os.getenv("LANGGRAPH_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
GHC_DT_MODEL = os.getenv("GHC_DT_MODEL", "gpt-4o-mini")
GHC_DT_TEMPERATURE = float(os.getenv("GHC_DT_TEMPERATURE", "0.2"))
GHC_DT_EVIDENCE_LOG = os.getenv("GHC_DT_EVIDENCE_LOG", "evidence.jsonl")

def load_state():
    """Load system state from file."""
    default_state = {
        "phase": "Phase 1: Pre-Operational Setup",
        "zec_rate": 4,
        "cash_buffer_to": "2026-06-30",
        "key_dates": {
            "phase1_start": "2025-01-01",
            "phase2_start": "2025-07-01",
            "phase3_start": "2026-01-01"
        }
    }
    
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default_state
    return default_state

def save_state(state):
    """Save system state to file."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        st.error(f"Failed to save state: {e}")

def log_evidence(entry):
    """Append to evidence log."""
    try:
        with open(EVIDENCE_FILE, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except IOError as e:
        st.error(f"Failed to log evidence: {e}")

# --- API Communication ---
def call_langgraph(question, command, agent, state):
    """Call LangGraph API."""
    headers = {"Content-Type": "application/json"}
    
    if LANGGRAPH_API_KEY:
        headers["Authorization"] = f"Bearer {LANGGRAPH_API_KEY}"
    
    payload = {
        "question": question,
        "command": command,
        "agent": agent,
        "state": state
    }
    
    try:
        response = requests.post(f"{LANGGRAPH_API_URL}/invoke", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Fallback a modo demo si hay error de API
        if "403" in str(e) or "Forbidden" in str(e):
            return {
                "answer": f"🔧 MODO DEMO: {AGENTS.get(agent, agent)} está procesando: '{question}'\n\n"
                         f"⚠️ API no disponible temporalmente. Para activar funcionalidad completa:\n"
                         f"1. Verificar API key en LangSmith\n"
                         f"2. Generar nueva API key si es necesario\n"
                         f"3. Actualizar configuración en .streamlit/secrets.toml",
                "meta": {"agent": agent, "mode": "demo"}
            }
        return {"status": "error", "message": f"API connection error: {e}"}

def test_langgraph_connection():
    """Test LangGraph API connection."""
    try:
        headers = {}
        if LANGGRAPH_API_KEY:
            headers["Authorization"] = f"Bearer {LANGGRAPH_API_KEY}"
        
        response = requests.get(f"{LANGGRAPH_API_URL}/health", headers=headers, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def test_openai_connection():
    """Test OpenAI API connection."""
    if not OPENAI_API_KEY:
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        client.models.list()
        return True
    except Exception:
        return False

# --- Session State Initialization ---
if 'lang' not in st.session_state:
    st.session_state.lang = None

if 'state' not in st.session_state:
    st.session_state.state = load_state()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- UI Rendering ---
# Language selection screen
if st.session_state.lang is None:
    st.markdown("# 🌿 Green Hill Cockpit")
    st.markdown("### Select Language / Seleccionar Idioma / Velja Tungumál / Choisir la Langue")
    
    cols = st.columns(4)
    languages = {"en": "🇬🇧 English", "es": "🇪🇸 Español", "is": "🇮🇸 Íslenska", "fr": "🇫🇷 Français"}
    
    for i, (code, name) in enumerate(languages.items()):
        if cols[i].button(name, use_container_width=True):
            st.session_state.lang = code
            st.rerun()
    st.stop()

# Main application UI
L = LANG[st.session_state.lang]

st.title(f"🌿 {L['title']}")
st.caption(L['subtitle'])

# Sidebar
with st.sidebar:
    st.header(L['select_agent'])
    
    agent_keys = list(AGENTS.keys())
    agent_display_names = [AGENTS[k] for k in agent_keys]
    selected_agent_display = st.selectbox("Agent:", options=agent_display_names, label_visibility="collapsed")
    selected_agent_key = agent_keys[agent_display_names.index(selected_agent_display)]
    
    command_keys = ["Auto"] + list(COMMANDS.keys())
    command_display_names = ["Auto"] + [COMMANDS[k] for k in COMMANDS.keys()]
    selected_command_display = st.selectbox("Command:", options=command_display_names)
    selected_command_key = command_keys[command_display_names.index(selected_command_display)]
    
    if selected_command_key == "Auto":
        selected_command_key = None
    
    with st.expander(L['governance_title'], expanded=False):
        st.write(f"**{L['phase']}:** {st.session_state.state.get('phase')}")
        st.write(f"**{L['zec_rate']}:** {st.session_state.state.get('zec_rate')}%")
        st.write(f"**{L['cash_buffer']}:** {st.session_state.state.get('cash_buffer_to')}")
    
    if st.button("🌐 " + L['select_language']):
        st.session_state.lang = None
        st.rerun()

# Main content tabs
tab_chat, tab_ingest, tab_evidence, tab_governance, tab_diagnostics, tab_code = st.tabs(L['tabs'])

with tab_chat:
    if not st.session_state.messages:
        st.info(L['shareholder_intro'])
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "agent" in msg:
                st.caption(f"Agent: {msg['agent']}")
    
    if query := st.chat_input(L['ask']):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)
        
        with st.spinner("..."):
            result = call_langgraph(query, selected_command_key, selected_agent_key, st.session_state.state)
        
        if result.get("status") == "error":
            st.error(f"Error: {result.get('message')}")
        else:
            answer = result.get("answer", "No response found.")
            agent_used = result.get("meta", {}).get("agent", selected_agent_key)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer, 
                "agent": AGENTS.get(agent_used, agent_used)
            })
            
            with st.chat_message("assistant"):
                st.write(answer)
                st.caption(f"Agent: {AGENTS.get(agent_used, agent_used)}")
            
            log_evidence({
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "agent": agent_used,
                "command": selected_command_key,
                "answer": answer,
                "state": st.session_state.state
            })

with tab_ingest:
    st.header(L['ingest_title'])
    st.info("Knowledge ingestion functionality is under development.")

with tab_evidence:
    st.header(L['evidence_title'])
    
    if os.path.exists(EVIDENCE_FILE):
        try:
            with open(EVIDENCE_FILE, 'r') as f:
                lines = f.readlines()
            
            for line in reversed(lines[-20:]):
                entry = json.loads(line)
                with st.expander(f"{entry['timestamp']} - {AGENTS.get(entry['agent'], entry['agent'])}"):
                    st.json(entry)
        except Exception as e:
            st.error(f"Could not read evidence file: {e}")
    else:
        st.info("No evidence has been logged yet.")

with tab_governance:
    st.header(L['governance_title'])
    st.info("Governance controls are under development.")

with tab_diagnostics:
    st.header(L['diagnostics_title'])
    
    col1, col2 = st.columns(2)
    
    if col1.button(L['test_langgraph']):
        with st.spinner("Testing LangGraph connection..."):
            if test_langgraph_connection():
                st.success("✅ LangGraph API is accessible")
            else:
                st.error("❌ LangGraph API connection failed")
                st.warning("🔧 Running in DEMO mode. Check API key configuration.")
    
    if col2.button(L['test_openai']):
        with st.spinner("Testing OpenAI connection..."):
            if test_openai_connection():
                st.success("✅ OpenAI API is accessible")
            else:
                st.error("❌ OpenAI API not accessible")
    
    st.subheader("Configuration")
    config_data = {
        "LANGGRAPH_API_URL": LANGGRAPH_API_URL,
        "LANGGRAPH_API_KEY": "********" if LANGGRAPH_API_KEY else "Not Set",
        "OPENAI_API_KEY": "********" if OPENAI_API_KEY else "Not Set",
        "Selected Agent": selected_agent_display,
        "Language": st.session_state.lang.upper()
    }
    st.json(config_data)
    
    # API Status info
    st.subheader("API Status Help")
    st.info("""
    **If LangGraph API shows ❌:**
    1. Check your API key in LangSmith dashboard
    2. Verify the URL matches your deployment
    3. Generate a new API key if needed
    4. Ensure proper project permissions
    
    **The app will run in DEMO mode until API is configured.**
    """)

with tab_code:
    st.header(L['code_title'])
    
    if query := st.text_area("Technical question for the Code Agent:"):
        if st.button("Ask Code Agent"):
            with st.spinner("Consulting Code Agent..."):
                result = call_langgraph(query, None, "code", st.session_state.state)
                
                if result.get("status") != "error":
                    st.code(result.get("answer", "# No code returned"), language="python")
                else:
                    st.error(result.get("message"))

# --- Footer ---
st.divider()
st.caption("Green Hill Executive Cockpit v2.1 | Powered by LangGraph & OpenAI")
