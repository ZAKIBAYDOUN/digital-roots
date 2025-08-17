import streamlit as st
import json
import os
import io
from datetime import datetime
import pandas as pd
import requests
import tempfile
from PIL import Image

# === IMPORTS CONDICIONALES ===
SPEECH_AVAILABLE = False
OCR_AVAILABLE = False
WEB_SEARCH_AVAILABLE = False
CV2_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    pass

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    pass

try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    pass

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    pass

# === CONFIGURACIÓN ===
STATE_FILE = "state.json"
LOG_FILE = "evidence.jsonl"
UPLOADS_DIR = "uploads"

# Crear directorio si no existe
os.makedirs(UPLOADS_DIR, exist_ok=True)

# === CONFIGURACIÓN MULTIMEDIA ===
MULTIMEDIA_STATUS = {
    "audio": SPEECH_AVAILABLE,
    "ocr": OCR_AVAILABLE, 
    "web_search": WEB_SEARCH_AVAILABLE,
    "opencv": CV2_AVAILABLE
}

# === CONFIGURACIÓN DE AGENTES ===
NATURAL_PROMPTS = {
    "CEO-DT": {
        "system": "Eres el CEO Digital Twin de Green Hill Canarias. Respondes como un ejecutivo experimentado.",
        "style": "Ejecutivo estratégico"
    },
    "FP&A": {
        "system": "Eres el analista financiero senior de Green Hill Canarias. Hablas con claridad sobre números.",
        "style": "Analista financiero senior"
    },
    "QA/Validation": {
        "system": "Eres el especialista en calidad y validación de Green Hill Canarias.",
        "style": "Especialista en calidad"
    },
    "Governance": {
        "system": "Eres el especialista en gobernanza corporativa de Green Hill Canarias.",
        "style": "Especialista en gobernanza"
    }
}

# === FUNCIONES MULTIMEDIA ===
def process_audio_input(audio_data):
    """Procesa audio y convierte a texto"""
    if not SPEECH_AVAILABLE:
        return "❌ Reconocimiento de voz no disponible. Instala: pip install speechrecognition"
    
    try:
        recognizer = sr.Recognizer()
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_data.getvalue())
            tmp_path = tmp_file.name
        
        # Reconocer texto
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language='es-ES')
            except:
                text = recognizer.recognize_google(audio, language='en-US')
            
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        return text
        
    except Exception as e:
        return f"❌ Error procesando audio: {str(e)}"

def process_image_input(image_data):
    """Procesa imagen y extrae texto usando OCR"""
    if not OCR_AVAILABLE:
        return {"error": "❌ OCR no disponible. Instala: pip install pytesseract"}
    
    try:
        image = Image.open(image_data)
        
        result = {
            "format": image.format,
            "size": image.size,
            "mode": image.mode,
            "extracted_text": ""
        }
        
        # Extraer texto
        text = pytesseract.image_to_string(image, lang='spa+eng')
        result["extracted_text"] = text.strip()
        
        return result
        
    except Exception as e:
        return {"error": f"❌ Error procesando imagen: {str(e)}"}

def web_research(query, max_results=5):
    """Busca información en internet"""
    if not WEB_SEARCH_AVAILABLE:
        return "❌ Búsqueda web no disponible. Instala: pip install duckduckgo-search"
    
    try:
        ddgs = DDGS()
        results = []
        
        for result in ddgs.text(query, max_results=max_results):
            results.append({
                "title": result.get("title", "Sin título"),
                "body": result.get("body", "Sin descripción"),
                "url": result.get("href", "")
            })
        
        if results:
            formatted_results = f"🔍 **Resultados para:** {query}\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"**{i}. {result['title']}**\n"
                formatted_results += f"{result['body']}\n"
                formatted_results += f"🔗 {result['url']}\n\n"
            return formatted_results
        else:
            return f"❌ No se encontraron resultados para: {query}"
            
    except Exception as e:
        return f"❌ Error en búsqueda web: {str(e)}"

def generate_research_report(topic, research_data, agent):
    """Genera informe de investigación"""
    
    agent_greeting = {
        "CEO-DT": "Como CEO de Green Hill Canarias",
        "FP&A": "Desde la perspectiva financiera", 
        "QA/Validation": "En términos de calidad y validación",
        "Governance": "Desde el punto de vista de gobernanza"
    }.get(agent, "Como especialista de Green Hill Canarias")
    
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    report = f"""# 📊 INFORME DE INVESTIGACIÓN

**Tema:** {topic}  
**Generado por:** {agent}  
**Fecha:** {current_time}

---

{agent_greeting}, he realizado una investigación sobre "{topic}".

## 🔍 INFORMACIÓN RECOPILADA
{research_data}

## 🎯 ANÁLISIS PARA GREEN HILL CANARIAS

### Relevancia Estratégica
- Alineación con objetivos de Phase I — Pilot & Shadow Mode
- Potencial impacto en compliance EU-GMP
- Oportunidades en el corredor atlántico

### Recomendaciones
1. **Evaluación técnica** detallada
2. **Análisis de viabilidad** financiera  
3. **Validación regulatoria** con equipo QA

## 📈 PRÓXIMOS PASOS
- Análisis profundo con equipos especializados
- Consulta con stakeholders clave
- Desarrollo de plan de acción

---
*Generado por Green Hill Cockpit Multimedia*
"""
    
    return report

# === CONEXIÓN LANGGRAPH ===
def _get_langgraph_app():
    """Obtiene la aplicación LangGraph"""
    try:
        from app.ghc_twin import app
        return app
    except ImportError:
        return None

def extract_natural_response(result, agent, query):
    """Extrae y mejora respuesta de LangGraph"""
    
    greetings = {
        "CEO-DT": "Como CEO de Green Hill Canarias",
        "FP&A": "Desde la perspectiva financiera",
        "QA/Validation": "En términos de calidad y validación", 
        "Governance": "Desde el punto de vista de gobernanza"
    }
    
    greeting = greetings.get(agent, "Como parte del equipo de Green Hill Canarias")
    
    if isinstance(result, dict) and "final_answer" in result:
        raw_answer = result["final_answer"]
        
        # Limpiar formato técnico
        cleaned = raw_answer.replace("###", "").replace("```", "").replace("Question:", "").strip()
        
        # Si es muy técnico, humanizar
        if "Summary:" in cleaned or len(cleaned) > 200:
            lines = cleaned.split('\n')
            useful_lines = [line for line in lines if line.strip() and not line.startswith('#')]
            
            if useful_lines:
                key_info = []
                for line in useful_lines[:3]:  # Primeras 3 líneas útiles
                    if any(emoji in line for emoji in ['��', '💰', '📊', '⚙️']):
                        clean_line = line.replace('- ', '').replace('|', ',').strip()
                        if len(clean_line) > 10:
                            key_info.append(clean_line)
                
                if key_info:
                    return f"{greeting}, he analizado tu consulta.\n\n" + "\n\n".join(key_info)
        
        return f"{greeting},\n\n{cleaned}"
    else:
        return f"{greeting}, he recibido tu consulta '{query}'. Los sistemas están procesando la información."

def run_command(query, mode, agent, multimedia_context=""):
    """Ejecuta comando con contexto multimedia"""
    app = _get_langgraph_app()
    
    # Agregar contexto multimedia si existe
    enhanced_query = query
    if multimedia_context:
        enhanced_query = f"{query}\n\n**Contexto multimedia:**\n{multimedia_context}"
    
    if app is None:
        agent_config = NATURAL_PROMPTS.get(agent, NATURAL_PROMPTS["CEO-DT"])
        response = f"🔴 **Sistema Offline**\n\nHola, soy el {agent_config['style']} de Green Hill Canarias.\n\nConsulta recibida: *'{query}'*"
        
        if multimedia_context:
            response += f"\n\n{multimedia_context}"
            
        response += "\n\nEl sistema LangGraph se está inicializando. Pronto estaré completamente operativo."
        
        return {"answer": response, "refs": ["sistema_offline"]}
    
    try:
        payload = {
            "question": enhanced_query,
            "source_type": "investor" if agent == "CEO-DT" else "master",
            "agent": agent,
            "command": mode,
            "state": get_state()
        }
        
        result = app.invoke(payload)
        natural_answer = extract_natural_response(result, agent, query)
        
        return {
            "answer": natural_answer,
            "refs": result.get("refs", []) if isinstance(result, dict) else []
        }
        
    except Exception as e:
        agent_style = NATURAL_PROMPTS.get(agent, NATURAL_PROMPTS["CEO-DT"])["style"]
        return {
            "answer": f"🔧 **Error Técnico**\n\nSoy el {agent_style} de Green Hill Canarias.\n\nError procesando: *'{query}'*\n\n**Error:** {type(e).__name__}",
            "refs": ["error_tecnico"]
        }

# === FUNCIONES DE ESTADO ===
def get_state():
    """Obtiene el estado actual del sistema"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    
    return {
        "phase": "Phase I — Pilot & Shadow Mode",
        "zec_rate": 4.0,
        "cash_buffer_to": "",
        "key_dates": {
            "zec_filing": "",
            "gmp_dossier": "", 
            "cash_buffer_to": ""
        }
    }

def set_state(key, value):
    """Actualiza el estado del sistema"""
    state = get_state()
    state[key] = value
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_log():
    """Obtiene el log de evidencia"""
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["timestamp", "agent", "action", "query", "answer", "refs"])
    
    rows = []
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["timestamp", "agent", "action", "query", "answer", "refs"])

def append_log(entry):
    """Añade entrada al log de evidencia"""
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass  # Fallar silenciosamente si no se puede escribir

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="🌿 Green Hill Cockpit Multimedia",
    layout="wide",
    page_icon="🎤"
)

# === VERIFICAR ESTADO DE LANGGRAPH ===
app_status = _get_langgraph_app()
connection_status = "🟢 CONNECTED" if app_status else "🔴 BUILDING..."

# === SIDEBAR ===
st.sidebar.title("⚙️ Control Panel")
st.sidebar.info(f"LangGraph: {connection_status}")

# Estado multimedia
st.sidebar.subheader("📱 Capacidades Multimedia")
multimedia_indicators = [
    ("🎤 Audio", MULTIMEDIA_STATUS["audio"]),
    ("📷 OCR", MULTIMEDIA_STATUS["ocr"]),
    ("🌐 Web Search", MULTIMEDIA_STATUS["web_search"]),
    ("�� OpenCV", MULTIMEDIA_STATUS["opencv"])
]

for label, status in multimedia_indicators:
    if status:
        st.sidebar.success(f"{label}: Activo")
    else:
        st.sidebar.error(f"{label}: No disponible")

# Controles principales
mode = st.sidebar.radio("Command", ["/brief", "/deep", "/action", "/sync", "/evidence", "/console", "/research"])
agent = st.sidebar.selectbox("Target Agent", ["CEO-DT", "FP&A", "QA/Validation", "Governance"])

if agent in NATURAL_PROMPTS:
    st.sidebar.info(f"**{NATURAL_PROMPTS[agent]['style']}**")

# Variables de estado
st.sidebar.subheader("Variables")
state = get_state()
phase = st.sidebar.text_input("Phase", state.get("phase", ""))
zec = st.sidebar.number_input("ZEC Rate (%)", value=float(state.get("zec_rate", 4.0)))

if st.sidebar.button("💾 Save Variables"):
    set_state("phase", phase)
    set_state("zec_rate", zec)
    st.sidebar.success("Estado actualizado ✅")

# === TABS PRINCIPALES ===
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "🎤 Audio", "📷 Visual", "🌐 Research", "📊 Reports"])

# === TAB 1: CHAT ===
with tab1:
    st.header("💬 Chat with Agents")
    st.subheader(f"Conversando con: **{agent}** | Modo: **{mode}**")
    
    # Inicializar historial
    if "history" not in st.session_state:
        st.session_state["history"] = []
    
    # Mostrar historial
    for turn in st.session_state["history"]:
        with st.chat_message("user"):
            st.write(turn['q'])
        with st.chat_message("assistant"):
            st.write(turn['a'])
    
    # Input de chat
    query = st.chat_input("Pregunta o instrucción para el agente...")
    
    if query:
        # Mostrar pregunta del usuario
        with st.chat_message("user"):
            st.write(query)
        
        # Procesar y mostrar respuesta
        with st.chat_message("assistant"):
            with st.spinner(f"⚡ {agent} está analizando..."):
                resp = run_command(query, mode, agent)
                answer = resp["answer"]
                st.write(answer)
        
        # Guardar en historial y log
        st.session_state["history"].append({"q": query, "a": answer, "agent": agent})
        append_log({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "action": mode,
            "query": query,
            "answer": answer,
            "refs": resp.get("refs", [])
        })
        st.rerun()

# === TAB 2: AUDIO ===
with tab2:
    st.header("🎤 Audio Input & Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Procesamiento de Audio")
        
        if MULTIMEDIA_STATUS["audio"]:
            audio_file = st.file_uploader("Cargar archivo de audio", type=['wav', 'mp3', 'm4a', 'ogg'])
            
            if audio_file:
                st.audio(audio_file)
                
                if st.button("🎤 Procesar Audio"):
                    with st.spinner("Convirtiendo audio a texto..."):
                        text = process_audio_input(audio_file)
                        
                        if not text.startswith("❌"):
                            st.success(f"**Texto extraído:** {text}")
                            
                            # Procesar con agente
                            with st.spinner("Analizando con agente..."):
                                resp = run_command(text, mode, agent, "📝 Texto extraído de audio")
                                st.write("**Respuesta del agente:**")
                                st.write(resp["answer"])
                        else:
                            st.error(text)
        else:
            st.error("🎤 Reconocimiento de voz no disponible")
            st.code("pip install speechrecognition")
    
    with col2:
        st.subheader("Grabación en Vivo")
        st.info("🚀 Próximamente: Grabación en tiempo real")

# === TAB 3: VISUAL ===
with tab3:
    st.header("📷 Visual Input & OCR")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Procesamiento de Imágenes")
        
        uploaded_image = st.file_uploader("Cargar imagen", type=['jpg', 'jpeg', 'png', 'bmp'])
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Imagen cargada", use_column_width=True)
            
            if st.button("🔍 Extraer Texto (OCR)"):
                with st.spinner("Procesando imagen..."):
                    result = process_image_input(uploaded_image)
                    
                    if "error" not in result:
                        st.json(result)
                        
                        if result.get("extracted_text"):
                            # Procesar con agente
                            with st.spinner("Analizando texto extraído..."):
                                resp = run_command(
                                    f"Analiza este texto extraído de imagen: {result['extracted_text']}", 
                                    mode, 
                                    agent, 
                                    "📷 Texto extraído de imagen via OCR"
                                )
                                st.write("**Análisis del agente:**")
                                st.write(resp["answer"])
                    else:
                        st.error(result["error"])
    
    with col2:
        st.subheader("Captura de Cámara")
        st.info("📷 Próximamente: Captura en tiempo real")

# === TAB 4: RESEARCH ===
with tab4:
    st.header("🌐 Web Research & Intelligence")
    
    research_query = st.text_input("🔍 Término de investigación:")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        research_focus = st.selectbox("Enfoque de investigación:", [
            "Biotecnología y cannabis",
            "Regulaciones EU-GMP", 
            "Mercado atlántico",
            "Innovación farmacéutica",
            "Compliance y calidad",
            "Investigación libre"
        ])
    
    with col2:
        max_results = st.number_input("Resultados", 1, 10, 5)
    
    if st.button("🚀 Investigar"):
        if research_query:
            with st.spinner("🔍 Buscando información..."):
                # Personalizar búsqueda según enfoque
                enhanced_query = research_query
                if research_focus != "Investigación libre":
                    enhanced_query = f"{research_query} {research_focus}"
                
                research_results = web_research(enhanced_query, max_results)
                st.write(research_results)
                
                # Analizar con agente si hay resultados
                if not research_results.startswith("❌"):
                    with st.spinner("Generando análisis estratégico..."):
                        resp = run_command(
                            f"Analiza esta investigación web para Green Hill Canarias: {research_query}", 
                            mode, 
                            agent, 
                            research_results
                        )
                        st.write("**Análisis estratégico:**")
                        st.write(resp["answer"])
        else:
            st.warning("Ingresa un término de investigación")

# === TAB 5: REPORTS ===
with tab5:
    st.header("📊 Research Reports & Evidence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Generar Informe")
        
        report_topic = st.text_input("📋 Tema del informe:")
        report_data = st.text_area("📄 Datos de investigación (opcional):")
        
        if st.button("📊 Generar Informe Completo"):
            if report_topic:
                # Investigar automáticamente si no hay datos
                if not report_data:
                    with st.spinner("Recopilando información..."):
                        report_data = web_research(report_topic, 5)
                
                # Generar informe
                with st.spinner("Generando informe..."):
                    report = generate_research_report(report_topic, report_data, agent)
                    st.markdown(report)
                    
                    # Opción de descarga
                    filename = f"informe_{report_topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                    st.download_button(
                        label="💾 Descargar Informe",
                        data=report,
                        file_name=filename,
                        mime="text/markdown"
                    )
            else:
                st.warning("Ingresa un tema para el informe")
    
    with col2:
        st.subheader("Evidence Log")
        
        df = get_log()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay evidencia registrada aún.")

# === FOOTER ===
st.markdown("---")
st.markdown("🌿 **Green Hill Cockpit Multimedia** - Powered by LangGraph & AI")
