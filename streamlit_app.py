import streamlit as st
import json, os
from datetime import datetime
import pandas as pd

STATE_FILE = "state.json"
LOG_FILE = "evidence.jsonl"

# === CONFIGURACIÓN LENGUAJE NATURAL ===
NATURAL_PROMPTS = {
    "CEO-DT": {
        "system": "Eres el CEO Digital Twin de Green Hill Canarias. Respondes como un ejecutivo experimentado, con lenguaje profesional pero accesible. Enfócate en decisiones estratégicas, oportunidades de negocio y visión a largo plazo.",
        "style": "Ejecutivo estratégico"
    },
    "FP&A": {
        "system": "Eres el analista financiero senior de Green Hill Canarias. Hablas con claridad sobre números, proyecciones y métricas financieras. Usa lenguaje preciso pero comprensible para stakeholders no financieros.",
        "style": "Analista financiero senior"
    },
    "QA/Validation": {
        "system": "Eres el especialista en calidad y validación de Green Hill Canarias. Respondes sobre procesos, compliance, GMP y estándares regulatorios con autoridad técnica pero lenguaje claro.",
        "style": "Especialista en calidad"
    },
    "Governance": {
        "system": "Eres el especialista en gobernanza corporativa de Green Hill Canarias. Hablas sobre estructura organizacional, políticas y marcos regulatorios con precisión legal pero lenguaje empresarial.",
        "style": "Especialista en gobernanza"
    }
}

def _get_langgraph_app():
    try:
        from app.ghc_twin import app
        return app
    except ImportError:
        return None

def run_command(query: str, mode: str, agent: str):
    app = _get_langgraph_app()
    if app is None:
        return {
            "answer": f"🔴 Hola, soy {agent} de Green Hill Canarias. Sistema en modo offline. Tu consulta: '{query or 'estado general'}' será procesada cuando LangGraph esté disponible.",
            "refs": ["sistema_offline"]
        }
    
    try:
        payload = {"question": query, "agent": agent, "command": mode, "state": get_state()}
        result = app.invoke(payload)
        return {"answer": str(result), "refs": []}
    except Exception as e:
        return {"answer": f"Error: {type(e).__name__}", "refs": ["error"]}

def get_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {"phase": "Phase I — Pilot & Shadow Mode", "zec_rate": 4.0, "cash_buffer_to": "", "key_dates": {"zec_filing": "", "gmp_dossier": "", "cash_buffer_to": ""}}

def set_state(key, value):
    state = get_state()
    state[key] = value
    json.dump(state, open(STATE_FILE, "w"), indent=2)

def get_log():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["timestamp","agent","action","query","answer","refs"])
    rows = []
    for line in open(LOG_FILE):
        try: rows.append(json.loads(line))
        except: continue
    return pd.DataFrame(rows)

def append_log(entry):
    with open(LOG_FILE,"a") as f: f.write(json.dumps(entry)+"\n")

st.set_page_config(page_title="🌿 Green Hill Cockpit", layout="wide")

app_status = _get_langgraph_app()
connection_status = "🟢 CONNECTED" if app_status else "🔴 BUILDING..."

st.sidebar.title("⚙️ Control Panel")
st.sidebar.info(f"LangGraph: {connection_status}")

mode = st.sidebar.radio("Command", ["/brief","/deep","/action","/sync","/evidence","/console"])
agent = st.sidebar.selectbox("Target Agent", ["CEO-DT","FP&A","QA/Validation","Governance"])

if agent in NATURAL_PROMPTS:
    st.sidebar.info(f"**{NATURAL_PROMPTS[agent]['style']}**")

st.sidebar.subheader("Variables")
state = get_state()
phase = st.sidebar.text_input("Phase", state.get("phase",""))
zec = st.sidebar.number_input("ZEC Rate (%)", value=float(state.get("zec_rate",4.0)))

if st.sidebar.button("💾 Save Variables"):
    set_state("phase", phase)
    set_state("zec_rate", zec)
    st.sidebar.success("Estado actualizado ✅")

tab1,tab2,tab3,tab4=st.tabs(["💬 Chat","📋 Actions","�� Evidence Log","🏛 Governance"])

with tab1:
    st.header("💬 Chat with Agents")
    st.subheader(f"Conversando con: **{agent}** | Modo: **{mode}**")
    
    if "history" not in st.session_state:
        st.session_state["history"] = []
        
    for turn in st.session_state["history"]:
        with st.chat_message("user"):
            st.write(turn['q'])
        with st.chat_message("assistant"):
            st.write(f"**{turn['agent']}:** {turn['a']}")
            
    q = st.chat_input("Pregunta o instrucción para el agente...")
    
    if q:
        with st.chat_message("user"):
            st.write(q)
            
        with st.chat_message("assistant"):
            resp = run_command(q, mode, agent)
            answer = resp["answer"]
            st.write(answer)
                
        st.session_state["history"].append({"q": q, "a": answer, "agent": agent})
        append_log({"timestamp": datetime.utcnow().isoformat(), "agent": agent, "action": mode, "query": q, "answer": answer, "refs": resp.get("refs",[])})
        st.rerun()

with tab2:
    st.header("📋 Tasks & Actions")
    resp = run_command("", "/action", agent)
    st.write(resp["answer"])

with tab3:
    st.header("📑 Evidence Log")
    df = get_log()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No hay evidencia registrada aún.")

with tab4:
    st.header("🏛 Governance & State")
    st.json(get_state())
