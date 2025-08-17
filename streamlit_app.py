import streamlit as st
import json, os
from datetime import datetime
import pandas as pd

STATE_FILE = "state.json"
LOG_FILE = "evidence.jsonl"

# === CONFIGURACIÓN LENGUAJE NATURAL ===
NATURAL_PROMPTS = {
    "CEO-DT": {
        "system": "Eres el CEO Digital Twin de Green Hill Canarias. Respondes como un ejecutivo experimentado, con lenguaje profesional pero accesible.",
        "style": "Ejecutivo estratégico"
    },
    "FP&A": {
        "system": "Eres el analista financiero senior de Green Hill Canarias. Hablas con claridad sobre números y proyecciones financieras.",
        "style": "Analista financiero senior"
    },
    "QA/Validation": {
        "system": "Eres el especialista en calidad y validación de Green Hill Canarias. Respondes sobre procesos, compliance y GMP.",
        "style": "Especialista en calidad"
    },
    "Governance": {
        "system": "Eres el especialista en gobernanza corporativa de Green Hill Canarias. Hablas sobre estructura organizacional y políticas.",
        "style": "Especialista en gobernanza"
    }
}

def _get_langgraph_app():
    try:
        from app.ghc_twin import app
        return app
    except ImportError:
        return None

def extract_natural_response(result, agent: str, query: str):
    """Extrae y mejora la respuesta de LangGraph para lenguaje natural"""
    
    # Diccionario de saludos por agente
    greetings = {
        "CEO-DT": "Como CEO de Green Hill Canarias",
        "FP&A": "Desde la perspectiva financiera",
        "QA/Validation": "En términos de calidad y validación",
        "Governance": "Desde el punto de vista de gobernanza"
    }
    
    greeting = greetings.get(agent, "Como parte del equipo de Green Hill Canarias")
    
    if isinstance(result, dict):
        # Extraer final_answer si existe
        if "final_answer" in result:
            raw_answer = result["final_answer"]
        # O buscar en diferentes campos posibles
        elif "answer" in result:
            raw_answer = result["answer"]
        elif "response" in result:
            raw_answer = result["response"]
        else:
            # Si no hay respuesta clara, crear una basada en outputs disponibles
            outputs = []
            if result.get("strategy_output", {}).get("analysis"):
                outputs.append(f"**Estrategia:** {result['strategy_output']['strategic_focus']}")
            if result.get("market_output", {}).get("analysis"):
                outputs.append(f"**Mercado:** {result['market_output']['market_opportunity']}")
            if result.get("finance_output", {}).get("analysis"):
                outputs.append(f"**Finanzas:** ROI proyectado disponible")
            
            if outputs:
                raw_answer = f"He analizado tu consulta '{query}'. Aquí mis hallazgos:\n\n" + "\n".join(outputs)
            else:
                raw_answer = f"He recibido tu consulta '{query}' y estoy procesando la información disponible."
    else:
        raw_answer = str(result)
    
    # Limpiar formato técnico
    if raw_answer and len(raw_answer) > 50:
        # Remover formato markdown excesivo
        cleaned = raw_answer.replace("###", "").replace("```", "")
        
        # Si parece ser una respuesta técnica, humanizarla
        if "Question:" in cleaned or "Summary:" in cleaned:
            # Extraer partes útiles y reformatear
            lines = cleaned.split('\n')
            useful_lines = [line for line in lines if line.strip() and not line.startswith('#') and 'Question:' not in line]
            
            if useful_lines:
                # Tomar las líneas más informativas
                key_info = []
                for line in useful_lines[:5]:  # Primeras 5 líneas útiles
                    if '🎯' in line or '💰' in line or '📊' in line or '⚙️' in line:
                        # Limpiar y agregar
                        clean_line = line.replace('- ', '').replace('|', ',').strip()
                        if len(clean_line) > 10:
                            key_info.append(clean_line)
                
                if key_info:
                    formatted_response = f"{greeting}, he analizado tu consulta.\n\n" + "\n\n".join(key_info)
                else:
                    formatted_response = f"{greeting}, estoy trabajando en tu consulta '{query}'. Los sistemas están procesando la información."
            else:
                formatted_response = f"{greeting}, he recibido tu consulta '{query}'. Permíteme brindarte una respuesta más detallada."
        else:
            # Si ya parece natural, solo agregar saludo
            formatted_response = f"{greeting},\n\n{cleaned}"
    else:
        # Respuesta muy corta o vacía
        formatted_response = f"{greeting}, he recibido tu consulta '{query}'. ¿Podrías ser más específico sobre lo que necesitas saber?"
    
    return formatted_response

def run_command(query: str, mode: str, agent: str):
    app = _get_langgraph_app()
    
    if app is None:
        agent_config = NATURAL_PROMPTS.get(agent, NATURAL_PROMPTS["CEO-DT"])
        return {
            "answer": f"🔴 **Sistema Temporalmente Offline**\n\nHola, soy el {agent_config['style']} de Green Hill Canarias.\n\nHe recibido tu consulta: *'{query or 'estado general'}'*\n\nActualmente el sistema LangGraph está inicializándose. Una vez conectado, podré brindarte un análisis completo y detallado.\n\n**Estado del proyecto:** Fase I — Pilot & Shadow Mode\n\nTe notificaré cuando esté completamente operativo.",
            "refs": ["sistema_offline"]
        }
    
    try:
        payload = {
            "question": query or "Estado general del proyecto",
            "source_type": "investor" if agent == "CEO-DT" else "master",
            "agent": agent,
            "command": mode,
            "state": get_state()
        }
        
        result = app.invoke(payload)
        
        # Extraer respuesta natural
        natural_answer = extract_natural_response(result, agent, query)
        
        return {
            "answer": natural_answer,
            "refs": result.get("refs", []) if isinstance(result, dict) else []
        }
        
    except Exception as e:
        return {
            "answer": f"🔧 **Error Técnico**\n\nSoy el {NATURAL_PROMPTS.get(agent, NATURAL_PROMPTS['CEO-DT'])['style']} de Green Hill Canarias.\n\nHe encontrado un problema al procesar: *'{query or 'tu consulta'}'*\n\n**Error:** {type(e).__name__}\n\nEl equipo técnico está resolviendo esto. Tu consulta ha sido registrada.",
            "refs": ["error_tecnico"]
        }

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

tab1,tab2,tab3,tab4=st.tabs(["💬 Chat","📋 Actions","📑 Evidence Log","🏛 Governance"])

with tab1:
    st.header("💬 Chat with Agents")
    st.subheader(f"Conversando con: **{agent}** | Modo: **{mode}**")
    
    if "history" not in st.session_state:
        st.session_state["history"] = []
        
    for turn in st.session_state["history"]:
        with st.chat_message("user"):
            st.write(turn['q'])
        with st.chat_message("assistant"):
            st.write(turn['a'])  # Ya no agregamos el prefijo del agente aquí
            
    q = st.chat_input("Pregunta o instrucción para el agente...")
    
    if q:
        with st.chat_message("user"):
            st.write(q)
            
        with st.chat_message("assistant"):
            with st.spinner(f"⚡ {agent} está analizando tu consulta..."):
                resp = run_command(q, mode, agent)
                answer = resp["answer"]
                st.write(answer)
                
        st.session_state["history"].append({"q": q, "a": answer, "agent": agent})
        append_log({"timestamp": datetime.utcnow().isoformat(), "agent": agent, "action": mode, "query": q, "answer": answer, "refs": resp.get("refs",[])})
        st.rerun()

with tab2:
    st.header("📋 Tasks & Actions")
    with st.spinner(f"⚡ Consultando tareas con {agent}..."):
        resp = run_command("", "/action", agent)
        st.write(resp["answer"])

with tab3:
    st.header("�� Evidence Log")
    df = get_log()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No hay evidencia registrada aún.")

with tab4:
    st.header("🏛 Governance & State")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Estado del Sistema")
        st.json(get_state())
    with col2:
        st.subheader("Agentes Disponibles")
        for agent_name, config in NATURAL_PROMPTS.items():
            st.write(f"**{agent_name}**: {config['style']}")
