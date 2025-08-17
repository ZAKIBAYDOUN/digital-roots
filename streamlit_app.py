import streamlit as st
import json, os, io
from datetime import datetime
import pandas as pd
import requests
from PIL import Image
import base64
import tempfile
import numpy as np

# Imports condicionales para funcionalidades multimedia
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False

STATE_FILE = "state.json"
LOG_FILE = "evidence.jsonl"
UPLOADS_DIR = "uploads"

# Crear directorio de uploads
os.makedirs(UPLOADS_DIR, exist_ok=True)

# === CONFIGURACIÓN MULTIMEDIA ===
MULTIMEDIA_CONFIG = {
    "audio": {
        "enabled": SPEECH_AVAILABLE,
        "formats": ["wav", "mp3", "m4a", "ogg"],
        "max_duration": 300  # 5 minutos
    },
    "image": {
        "enabled": OPENCV_AVAILABLE and OCR_AVAILABLE,
        "formats": ["jpg", "jpeg", "png", "bmp", "tiff"],
        "max_size": 10  # 10MB
    },
    "camera": {
        "enabled": OPENCV_AVAILABLE,
        "resolution": (640, 480)
    },
    "web_research": {
        "enabled": WEB_SEARCH_AVAILABLE,
        "max_results": 10
    }
}

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

# === FUNCIONES MULTIMEDIA ===

def process_audio_input(audio_data):
    """Procesa audio y convierte a texto usando speech recognition"""
    if not SPEECH_AVAILABLE:
        return "❌ Reconocimiento de voz no disponible. Instalar: pip install speechrecognition pyaudio"
    
    try:
        recognizer = sr.Recognizer()
        
        # Guardar audio temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_data.getvalue())
            tmp_path = tmp_file.name
        
        # Reconocer texto
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language='es-ES')
            
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
        return text
        
    except Exception as e:
        return f"❌ Error procesando audio: {type(e).__name__}"

def process_image_input(image_data, ocr_enabled=True):
    """Procesa imagen y extrae texto usando OCR"""
    if not OCR_AVAILABLE and ocr_enabled:
        return "❌ OCR no disponible. Instalar: pip install pytesseract"
    
    try:
        image = Image.open(image_data)
        
        # Información básica de la imagen
        info = {
            "format": image.format,
            "size": image.size,
            "mode": image.mode,
            "extracted_text": ""
        }
        
        # Extraer texto si OCR está habilitado
        if ocr_enabled and OCR_AVAILABLE:
            text = pytesseract.image_to_string(image, lang='spa+eng')
            info["extracted_text"] = text.strip()
        
        return info
        
    except Exception as e:
        return f"❌ Error procesando imagen: {type(e).__name__}"

def capture_camera_image():
    """Captura imagen desde cámara"""
    if not OPENCV_AVAILABLE:
        return None, "❌ OpenCV no disponible. Instalar: pip install opencv-python-headless"
    
    try:
        # Simular captura (en producción usaría streamlit-webrtc)
        return None, "📷 Funcionalidad de cámara configurada. Usar streamlit-webrtc para captura en vivo."
        
    except Exception as e:
        return None, f"❌ Error capturando imagen: {type(e).__name__}"

def web_research(query, max_results=5):
    """Busca información en internet usando DuckDuckGo"""
    if not WEB_SEARCH_AVAILABLE:
        return "❌ Búsqueda web no disponible. Instalar: pip install duckduckgo-search"
    
    try:
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(f"{query} Green Hill Canarias biotechnology", max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "body": result.get("body", ""),
                    "url": result.get("href", "")
                })
            
            if results:
                formatted_results = f"🔍 **Resultados de investigación para:** {query}\n\n"
                for i, result in enumerate(results, 1):
                    formatted_results += f"**{i}. {result['title']}**\n{result['body']}\n🔗 {result['url']}\n\n"
                return formatted_results
            else:
                return f"❌ No se encontraron resultados para: {query}"
                
    except Exception as e:
        return f"❌ Error en búsqueda web: {type(e).__name__}"

def generate_research_report(topic, research_data, agent):
    """Genera informe de investigación basado en datos recopilados"""
    
    greeting = {
        "CEO-DT": "Como CEO de Green Hill Canarias",
        "FP&A": "Desde la perspectiva financiera",
        "QA/Validation": "En términos de calidad y validación",
        "Governance": "Desde el punto de vista de gobernanza"
    }.get(agent, "Como especialista de Green Hill Canarias")
    
    report = f"""# 📊 INFORME DE INVESTIGACIÓN
**Tema:** {topic}
**Generado por:** {agent}
**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

---

{greeting}, he realizado una investigación exhaustiva sobre "{topic}".

## 🔍 DATOS RECOPILADOS
{research_data}

## 🎯 ANÁLISIS ESTRATÉGICO
Basándome en la información recopilada, puedo identificar las siguientes implicaciones para Green Hill Canarias:

### Oportunidades Identificadas
- Alineación con objetivos estratégicos de la empresa
- Potencial de innovación en biotecnología
- Sinergias con el mercado atlántico

### Recomendaciones
1. **Evaluación detallada** de viabilidad técnica y financiera
2. **Análisis de compliance** con regulaciones EU-GMP
3. **Estudio de mercado** en el corredor atlántico

## 📈 PRÓXIMOS PASOS
- Análisis más profundo con el equipo técnico
- Validación con stakeholders clave
- Desarrollo de plan de implementación

---
*Informe generado por Green Hill Cockpit Multimedia*
"""
    
    return report

# === CONEXIÓN LANGGRAPH ===
def _get_langgraph_app():
    try:
        from app.ghc_twin import app
        return app
    except ImportError:
        return None

def extract_natural_response(result, agent: str, query: str):
    """Extrae respuesta natural de LangGraph"""
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
        
        if len(cleaned) > 100:
            return f"{greeting},\n\n{cleaned}"
        else:
            return f"{greeting}, he procesado tu consulta.\n\n{cleaned}"
    else:
        return f"{greeting}, he recibido tu consulta '{query}'. Los sistemas están procesando la información."

def run_command(query: str, mode: str, agent: str, multimedia_context=""):
    """Ejecuta comando con contexto multimedia opcional"""
    app = _get_langgraph_app()
    
    # Agregar contexto multimedia al query si existe
    enhanced_query = query
    if multimedia_context:
        enhanced_query = f"{query}\n\n**Contexto multimedia:**\n{multimedia_context}"
    
    if app is None:
        agent_config = NATURAL_PROMPTS.get(agent, NATURAL_PROMPTS["CEO-DT"])
        return {
            "answer": f"🔴 **Sistema Temporalmente Offline**\n\nHola, soy el {agent_config['style']} de Green Hill Canarias.\n\nHe recibido tu consulta: *'{query}'*\n\n{multimedia_context}\n\nActualmente el sistema LangGraph está inicializándose. Una vez conectado, podré brindarte un análisis completo.\n\n**Estado del proyecto:** Fase I — Pilot & Shadow Mode",
            "refs": ["sistema_offline"]
        }
    
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
        return {
            "answer": f"🔧 **Error Técnico**\n\nSoy el {NATURAL_PROMPTS.get(agent, NATURAL_PROMPTS['CEO-DT'])['style']} de Green Hill Canarias.\n\nError al procesar: *'{query}'*\n\n**Error:** {type(e).__name__}",
            "refs": ["error_tecnico"]
        }

# === FUNCIONES BÁSICAS ===
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

# === UI PRINCIPAL ===
st.set_page_config(page_title="🌿 Green Hill Cockpit Multimedia", layout="wide", page_icon="🎤")

app_status = _get_langgraph_app()
connection_status = "🟢 CONNECTED" if app_status else "🔴 BUILDING..."

# === SIDEBAR ===
st.sidebar.title("⚙️ Control Panel")
st.sidebar.info(f"LangGraph: {connection_status}")

# Mostrar estado multimedia
st.sidebar.subheader("📱 Capacidades Multimedia")
if MULTIMEDIA_CONFIG["audio"]["enabled"]:
    st.sidebar.success("🎤 Audio: Activo")
else:
    st.sidebar.error("🎤 Audio: No disponible")

if MULTIMEDIA_CONFIG["image"]["enabled"]:
    st.sidebar.success("📷 Imagen/OCR: Activo")
else:
    st.sidebar.error("📷 Imagen/OCR: No disponible")

if MULTIMEDIA_CONFIG["web_research"]["enabled"]:
    st.sidebar.success("🌐 Investigación Web: Activa")
else:
    st.sidebar.error("🌐 Investigación Web: No disponible")

mode = st.sidebar.radio("Command", ["/brief","/deep","/action","/sync","/evidence","/console", "/research"])
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

# === TABS PRINCIPALES ===
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "🎤 Audio", "📷 Visual", "🌐 Research", "📊 Reports"])

with tab1:
    st.header("💬 Chat with Agents")
    st.subheader(f"Conversando con: **{agent}** | Modo: **{mode}**")
    
    if "history" not in st.session_state:
        st.session_state["history"] = []
        
    for turn in st.session_state["history"]:
        with st.chat_message("user"):
            st.write(turn['q'])
        with st.chat_message("assistant"):
            st.write(turn['a'])
            
    q = st.chat_input("Pregunta o instrucción para el agente...")
    
    if q:
        with st.chat_message("user"):
            st.write(q)
            
        with st.chat_message("assistant"):
            with st.spinner(f"⚡ {agent} está analizando..."):
                resp = run_command(q, mode, agent)
                answer = resp["answer"]
                st.write(answer)
                
        st.session_state["history"].append({"q": q, "a": answer, "agent": agent})
        append_log({"timestamp": datetime.utcnow().isoformat(), "agent": agent, "action": mode, "query": q, "answer": answer, "refs": resp.get("refs",[])})
        st.rerun()

with tab2:
    st.header("🎤 Audio Input & Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Grabación de Audio")
        if SPEECH_AVAILABLE:
            audio_file = st.file_uploader("Cargar archivo de audio", type=['wav', 'mp3', 'm4a', 'ogg'])
            if audio_file:
                st.audio(audio_file, format='audio/wav')
                if st.button("🎤 Procesar Audio"):
                    with st.spinner("Convirtiendo audio a texto..."):
                        text = process_audio_input(audio_file)
                        st.success(f"**Texto extraído:** {text}")
                        
                        # Procesar con agente
                        resp = run_command(text, mode, agent, "📝 Texto extraído de audio")
                        st.write("**Respuesta del agente:**")
                        st.write(resp["answer"])
        else:
            st.error("🎤 Reconocimiento de voz no disponible")
            st.code("pip install speechrecognition pyaudio")
    
    with col2:
        st.subheader("Grabación en Vivo")
        st.info("🚀 Próximamente: Grabación en tiempo real con streamlit-webrtc")

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
                    if isinstance(result, dict):
                        st.json(result)
                        if result.get("extracted_text"):
                            # Procesar texto extraído con agente
                            resp = run_command(f"Analiza este texto extraído de imagen: {result['extracted_text']}", mode, agent, "📷 Texto extraído de imagen via OCR")
                            st.write("**Análisis del agente:**")
                            st.write(resp["answer"])
                    else:
                        st.error(result)
    
    with col2:
        st.subheader("Captura de Cámara")
        if st.button("📸 Capturar desde Cámara"):
            image, msg = capture_camera_image()
            st.info(msg)

with tab4:
    st.header("🌐 Web Research & Intelligence")
    
    research_query = st.text_input("🔍 Término de investigación:")
    max_results = st.slider("Máximo resultados", 1, 20, 5)
    
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
        if st.button("🚀 Investigar"):
            if research_query:
                with st.spinner("🔍 Buscando información..."):
                    # Personalizar búsqueda según enfoque
                    enhanced_query = research_query
                    if research_focus != "Investigación libre":
                        enhanced_query = f"{research_query} {research_focus}"
                    
                    research_results = web_research(enhanced_query, max_results)
                    st.write(research_results)
                    
                    # Generar análisis con agente
                    if "❌" not in research_results:
                        resp = run_command(f"Analiza esta investigación web para Green Hill Canarias: {research_query}", mode, agent, research_results)
                        st.write("**Análisis estratégico:**")
                        st.write(resp["answer"])
            else:
                st.warning("Ingresa un término de investigación")

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
                report = generate_research_report(report_topic, report_data, agent)
                st.markdown(report)
                
                # Opción de descarga
                st.download_button(
                    label="💾 Descargar Informe",
                    data=report,
                    file_name=f"informe_{report_topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown"
                )
            else:
                st.warning("Ingresa un tema para el informe")
    
    with col2:
        st.subheader("Evidence Log Multimedia")
        df = get_log()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay evidencia registrada aún.")

# === FOOTER ===
st.markdown("---")
st.markdown("🌿 **Green Hill Cockpit Multimedia** - Powered by LangGraph & AI")
