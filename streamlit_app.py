import streamlit as st
import json
import os
import io
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional, List

import pandas as pd
import requests
from PIL import Image

# === IMPORTS CONDICIONALES SEGUROS ===
FEATURES = {
    "speech": False,
    "ocr": False, 
    "websearch": False,
    "opencv": False
}

# Speech Recognition
try:
    import speech_recognition as sr
    FEATURES["speech"] = True
except ImportError:
    sr = None

# OCR
try:
    import pytesseract
    FEATURES["ocr"] = True
except ImportError:
    pytesseract = None

# Web Search
try:
    from duckduckgo_search import DDGS
    FEATURES["websearch"] = True
except ImportError:
    DDGS = None

# OpenCV
try:
    import cv2
    import numpy as np
    FEATURES["opencv"] = True
except ImportError:
    cv2 = None
    np = None

# === CONFIGURACIÓN ===
STATE_FILE = "state.json"
LOG_FILE = "evidence.jsonl"
UPLOADS_DIR = "uploads"

# Crear directorio uploads
os.makedirs(UPLOADS_DIR, exist_ok=True)

# === CONFIGURACIÓN DE AGENTES ===
AGENT_CONFIGS = {
    "CEO-DT": {
        "name": "CEO Digital Twin",
        "role": "Ejecutivo Estratégico",
        "greeting": "Como CEO de Green Hill Canarias"
    },
    "FP&A": {
        "name": "Financial Planning & Analysis",
        "role": "Analista Financiero Senior", 
        "greeting": "Desde la perspectiva financiera"
    },
    "QA/Validation": {
        "name": "Quality Assurance & Validation",
        "role": "Especialista en Calidad",
        "greeting": "En términos de calidad y validación"
    },
    "Governance": {
        "name": "Corporate Governance",
        "role": "Especialista en Gobernanza",
        "greeting": "Desde el punto de vista de gobernanza"
    }
}

# === FUNCIONES MULTIMEDIA ===
def safe_process_audio(audio_data) -> str:
    """Procesa audio de manera segura"""
    if not FEATURES["speech"] or not sr:
        return "❌ Reconocimiento de voz no disponible. Instala: pip install speechrecognition pyaudio"
    
    try:
        recognizer = sr.Recognizer()
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_data.getvalue())
            tmp_path = tmp.name
        
        try:
            # Procesar audio
            with sr.AudioFile(tmp_path) as source:
                audio = recognizer.record(source)
                
            # Intentar español primero, luego inglés
            for lang in ['es-ES', 'en-US']:
                try:
                    text = recognizer.recognize_google(audio, language=lang)
                    return text
                except sr.UnknownValueError:
                    continue
                    
            return "❌ No se pudo reconocer el audio"
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        return f"❌ Error procesando audio: {str(e)}"

def safe_process_image(image_data) -> Dict[str, Any]:
    """Procesa imagen de manera segura"""
    if not FEATURES["ocr"] or not pytesseract:
        return {"error": "❌ OCR no disponible. Instala: pip install pytesseract"}
    
    try:
        image = Image.open(image_data)
        
        # Información básica
        result = {
            "format": str(image.format),
            "size": list(image.size),
            "mode": str(image.mode),
            "extracted_text": ""
        }
        
        # OCR con manejo de errores
        try:
            text = pytesseract.image_to_string(image, lang='spa+eng')
            result["extracted_text"] = text.strip()
        except Exception as ocr_error:
            result["ocr_error"] = str(ocr_error)
            
        return result
        
    except Exception as e:
        return {"error": f"❌ Error procesando imagen: {str(e)}"}

def safe_web_research(query: str, max_results: int = 5) -> str:
    """Búsqueda web segura"""
    if not FEATURES["websearch"] or not DDGS:
        return "❌ Búsqueda web no disponible. Instala: pip install duckduckgo-search"
    
    try:
        results = []
        search_query = f"{query} Green Hill Canarias biotechnology"
        
        # Búsqueda con timeout
        with DDGS() as ddgs:
            search_results = ddgs.text(search_query, max_results=max_results)
            
            for r in search_results:
                results.append({
                    "title": r.get("title", "Sin título")[:100],
                    "body": r.get("body", "Sin descripción")[:200],
                    "url": r.get("href", "")
                })
        
        if not results:
            return f"❌ No se encontraron resultados para: {query}"
            
        # Formatear resultados
        formatted = f"🔍 **Resultados para:** {query}\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {result['title']}**\n"
            formatted += f"{result['body']}...\n"
            formatted += f"🔗 {result['url']}\n\n"
            
        return formatted
        
    except Exception as e:
        return f"❌ Error en búsqueda web: {str(e)}"

def generate_report(topic: str, data: str, agent: str) -> str:
    """Genera informe de investigación"""
    agent_config = AGENT_CONFIGS.get(agent, AGENT_CONFIGS["CEO-DT"])
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    return f"""# 📊 INFORME DE INVESTIGACIÓN

**Tema:** {topic}  
**Generado por:** {agent} ({agent_config['role']})  
**Fecha:** {current_time}

---

{agent_config['greeting']}, he realizado una investigación sobre "{topic}".

## 🔍 INFORMACIÓN RECOPILADA

{data}

## 🎯 ANÁLISIS PARA GREEN HILL CANARIAS

### Relevancia Estratégica
- Alineación con Phase I — Pilot & Shadow Mode
- Potencial impacto en compliance EU-GMP  
- Oportunidades en el corredor atlántico

### Recomendaciones
1. **Evaluación técnica** detallada
2. **Análisis de viabilidad** financiera
3. **Validación regulatoria** con equipo QA

## 📈 PRÓXIMOS PASOS
- Análisis profundo con equipos especializados
- Consulta con stakeholders clave
- Desarrollo de plan de implementación

---
*Generado por Green Hill Cockpit Multimedia*
"""

# === CONEXIÓN LANGGRAPH ===
def get_langgraph_app():
    """Obtiene la app LangGraph de forma segura"""
    try:
        from app.ghc_twin import app
        return app
    except ImportError:
        return None

def process_langgraph_response(result: Any, agent: str, query: str) -> str:
    """Procesa respuesta de LangGraph de manera natural"""
    agent_config = AGENT_CONFIGS.get(agent, AGENT_CONFIGS["CEO-DT"])
    greeting = agent_config["greeting"]
    
    if isinstance(result, dict) and "final_answer" in result:
        answer = result["final_answer"]
        
        # Limpiar formato técnico
        clean_answer = str(answer).replace("###", "").replace("```", "").strip()
        
        # Si es muy técnica o larga, extraer puntos clave
        if len(clean_answer) > 300 or "Summary:" in clean_answer:
            lines = [l.strip() for l in clean_answer.split('\n') if l.strip()]
            key_points = []
            
            for line in lines[:5]:  # Primeros 5 puntos
                if any(emoji in line for emoji in ['🎯', '💰', '📊', '⚙️', '•', '-']):
                    clean_line = line.replace('- ', '').replace('|', ' - ').strip()
                    if len(clean_line) > 15:
                        key_points.append(clean_line)
            
            if key_points:
                return f"{greeting}, he analizado tu consulta.\n\n" + "\n\n".join(key_points)
        
        return f"{greeting},\n\n{clean_answer}"
    
    return f"{greeting}, he recibido tu consulta '{query}'. Los sistemas están procesando la información disponible."

def execute_command(query: str, mode: str, agent: str, context: str = "") -> Dict[str, Any]:
    """Ejecuta comando principal con LangGraph"""
    app = get_langgraph_app()
    
    # Enriquecer query con contexto multimedia
    enhanced_query = query
    if context:
        enhanced_query = f"{query}\n\n**Contexto adicional:**\n{context}"
    
    # Si LangGraph no está disponible
    if not app:
        agent_config = AGENT_CONFIGS.get(agent, AGENT_CONFIGS["CEO-DT"])
        offline_response = f"🔴 **Sistema Temporalmente Offline**\n\n"
        offline_response += f"Hola, soy el {agent_config['role']} de Green Hill Canarias.\n\n"
        offline_response += f"Consulta recibida: *'{query}'*\n\n"
        
        if context:
            offline_response += f"{context}\n\n"
            
        offline_response += "El sistema LangGraph se está inicializando. Pronto podré darte un análisis completo."
        
        return {"answer": offline_response, "refs": ["sistema_offline"]}
    
    # Ejecutar con LangGraph
    try:
        payload = {
            "question": enhanced_query,
            "source_type": "investor" if agent == "CEO-DT" else "master",
            "agent": agent,
            "command": mode,
            "state": load_state()
        }
        
        result = app.invoke(payload)
        natural_answer = process_langgraph_response(result, agent, query)
        
        return {
            "answer": natural_answer,
            "refs": result.get("refs", []) if isinstance(result, dict) else []
        }
        
    except Exception as e:
        agent_config = AGENT_CONFIGS.get(agent, AGENT_CONFIGS["CEO-DT"])
        error_response = f"🔧 **Error Técnico**\n\n"
        error_response += f"Soy el {agent_config['role']} de Green Hill Canarias.\n\n"
        error_response += f"Error procesando: *'{query}'*\n\n"
        error_response += f"**Detalle:** {type(e).__name__}"
        
        return {"answer": error_response, "refs": ["error_tecnico"]}

# === FUNCIONES DE ESTADO ===
def load_state() -> Dict[str, Any]:
    """Carga el estado del sistema"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
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

def save_state(key: str, value: Any) -> None:
    """Guarda estado del sistema"""
    try:
        state = load_state()
        state[key] = value
        
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Fallar silenciosamente

def load_evidence_log() -> pd.DataFrame:
    """Carga log de evidencia"""
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["timestamp", "agent", "action", "query", "answer", "refs"])
    
    rows = []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
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

def append_to_log(entry: Dict[str, Any]) -> None:
    """Añade entrada al log"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass

# === CONFIGURACIÓN STREAMLIT ===
st.set_page_config(
    page_title="🌿 Green Hill Cockpit Multimedia",
    layout="wide",
    page_icon="🎤",
    initial_sidebar_state="expanded"
)

# === VERIFICAR ESTADO ===
langgraph_app = get_langgraph_app()
connection_status = "🟢 CONNECTED" if langgraph_app else "🔴 BUILDING..."

# === SIDEBAR ===
st.sidebar.title("⚙️ Control Panel")
st.sidebar.info(f"LangGraph: {connection_status}")

# Estado de funciones multimedia
st.sidebar.subheader("📱 Capacidades")
feature_labels = {
    "speech": "🎤 Audio",
    "ocr": "📷 OCR", 
    "websearch": "🌐 Web Search",
    "opencv": "🔧 OpenCV"
}

for key, label in feature_labels.items():
    if FEATURES[key]:
        st.sidebar.success(f"{label}: ✅")
    else:
        st.sidebar.error(f"{label}: ❌")

# Controles principales
mode = st.sidebar.radio(
    "Modo de Comando", 
    ["/brief", "/deep", "/action", "/sync", "/evidence", "/console", "/research"],
    help="Selecciona el tipo de análisis que deseas"
)

agent = st.sidebar.selectbox(
    "Agente Especializado", 
    list(AGENT_CONFIGS.keys()),
    help="Elige el especialista para tu consulta"
)

# Mostrar info del agente
if agent in AGENT_CONFIGS:
    st.sidebar.info(f"**{AGENT_CONFIGS[agent]['role']}**")

# Variables de estado del proyecto
st.sidebar.subheader("📊 Variables del Proyecto")
current_state = load_state()

phase = st.sidebar.text_input("Fase Actual", current_state.get("phase", ""))
zec_rate = st.sidebar.number_input("Tasa ZEC (%)", value=float(current_state.get("zec_rate", 4.0)), step=0.1)

if st.sidebar.button("💾 Guardar Variables"):
    save_state("phase", phase)
    save_state("zec_rate", zec_rate)
    st.sidebar.success("✅ Estado actualizado")

# === INTERFACE PRINCIPAL ===
st.title("🌿 Green Hill Cockpit Multimedia")
st.markdown(f"**Agente Activo:** {AGENT_CONFIGS[agent]['role']} | **Modo:** {mode}")

# === TABS ===
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat", 
    "🎤 Audio", 
    "📷 Visual", 
    "🌐 Research", 
    "📊 Reports"
])

# TAB 1: CHAT
with tab1:
    st.header("💬 Conversación con Agentes")
    
    # Inicializar historial
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Mostrar conversación
    for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(entry["question"])
        with st.chat_message("assistant"):
            st.write(entry["answer"])
    
    # Input principal
    user_input = st.chat_input("Escribe tu pregunta o instrucción...")
    
    if user_input:
        # Mostrar pregunta del usuario
        with st.chat_message("user"):
            st.write(user_input)
        
        # Procesar y mostrar respuesta
        with st.chat_message("assistant"):
            with st.spinner(f"⚡ {agent} está procesando..."):
                response = execute_command(user_input, mode, agent)
                answer = response["answer"]
                st.write(answer)
        
        # Guardar en historial y log
        st.session_state.chat_history.append({
            "question": user_input,
            "answer": answer,
            "agent": agent,
            "mode": mode
        })
        
        append_to_log({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "action": mode,
            "query": user_input,
            "answer": answer,
            "refs": response.get("refs", [])
        })
        
        st.rerun()

# TAB 2: AUDIO
with tab2:
    st.header("🎤 Procesamiento de Audio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if FEATURES["speech"]:
            st.subheader("📤 Cargar Audio")
            audio_file = st.file_uploader(
                "Selecciona archivo de audio",
                type=['wav', 'mp3', 'm4a', 'ogg'],
                help="Formatos soportados: WAV, MP3, M4A, OGG"
            )
            
            if audio_file:
                st.audio(audio_file)
                
                if st.button("🎤 Convertir a Texto"):
                    with st.spinner("🔄 Procesando audio..."):
                        text_result = safe_process_audio(audio_file)
                        
                        if not text_result.startswith("❌"):
                            st.success("✅ Texto extraído exitosamente")
                            st.write(f"**📝 Contenido:** {text_result}")
                            
                            # Procesar con agente
                            with st.spinner("🧠 Analizando contenido..."):
                                response = execute_command(
                                    text_result, 
                                    mode, 
                                    agent, 
                                    "📝 Contenido extraído de audio"
                                )
                                st.write("**🤖 Análisis del Agente:**")
                                st.write(response["answer"])
                        else:
                            st.error(text_result)
        else:
            st.error("🎤 Funcionalidad de audio no disponible")
            st.code("pip install speechrecognition pyaudio")
    
    with col2:
        st.subheader("ℹ️ Información")
        st.info("**Próximamente:**\n- Grabación en tiempo real\n- Múltiples idiomas\n- Mejora de calidad")

# TAB 3: VISUAL
with tab3:
    st.header("📷 Procesamiento Visual y OCR")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if FEATURES["ocr"]:
            st.subheader("📤 Cargar Imagen")
            image_file = st.file_uploader(
                "Selecciona imagen",
                type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
                help="Formatos soportados: JPG, PNG, BMP, TIFF"
            )
            
            if image_file:
                # Mostrar imagen
                image = Image.open(image_file)
                st.image(image, caption="Imagen cargada", use_container_width=True)
                
                if st.button("🔍 Extraer Texto (OCR)"):
                    with st.spinner("🔄 Procesando imagen..."):
                        ocr_result = safe_process_image(image_file)
                        
                        if "error" not in ocr_result:
                            st.success("✅ Imagen procesada exitosamente")
                            
                            # Mostrar información de la imagen
                            st.json(ocr_result)
                            
                            # Si hay texto extraído, analizarlo
                            if ocr_result.get("extracted_text"):
                                extracted_text = ocr_result["extracted_text"]
                                st.write(f"**📝 Texto extraído:** {extracted_text}")
                                
                                # Analizar con agente
                                with st.spinner("🧠 Analizando texto extraído..."):
                                    response = execute_command(
                                        f"Analiza este contenido: {extracted_text}",
                                        mode,
                                        agent,
                                        "📷 Texto extraído de imagen via OCR"
                                    )
                                    st.write("**🤖 Análisis del Agente:**")
                                    st.write(response["answer"])
                            else:
                                st.warning("⚠️ No se encontró texto en la imagen")
                        else:
                            st.error(ocr_result["error"])
        else:
            st.error("📷 Funcionalidad OCR no disponible")
            st.code("pip install pytesseract")
    
    with col2:
        st.subheader("ℹ️ Características OCR")
        st.info("""
        **Capacidades:**
        - Español e Inglés
        - Múltiples formatos
        - Análisis automático
        
        **Próximamente:**
        - Captura en vivo
        - Más idiomas
        - Detección de objetos
        """)

# TAB 4: RESEARCH
with tab4:
    st.header("🌐 Investigación Web")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        research_query = st.text_input(
            "🔍 ¿Qué quieres investigar?",
            placeholder="Ej: nuevas regulaciones EU-GMP 2025"
        )
        
        research_focus = st.selectbox(
            "🎯 Enfoque de investigación:",
            [
                "Investigación general",
                "Biotecnología y cannabis", 
                "Regulaciones EU-GMP",
                "Mercado atlántico",
                "Innovación farmacéutica",
                "Compliance y calidad"
            ]
        )
    
    with col2:
        max_results = st.number_input("📊 Número de resultados", 1, 15, 5)
        
        research_button = st.button("�� Investigar", use_container_width=True)
    
    if research_button and research_query:
        if FEATURES["websearch"]:
            with st.spinner("🔍 Buscando información..."):
                # Personalizar búsqueda
                enhanced_query = research_query
                if research_focus != "Investigación general":
                    enhanced_query = f"{research_query} {research_focus}"
                
                search_results = safe_web_research(enhanced_query, max_results)
                st.write(search_results)
                
                # Analizar resultados si son válidos
                if not search_results.startswith("❌"):
                    with st.spinner("🧠 Generando análisis estratégico..."):
                        analysis_query = f"Analiza esta investigación para Green Hill Canarias: {research_query}"
                        response = execute_command(
                            analysis_query,
                            mode, 
                            agent,
                            search_results
                        )
                        st.write("**🤖 Análisis Estratégico:**")
                        st.write(response["answer"])
        else:
            st.error("�� Búsqueda web no disponible")
            st.code("pip install duckduckgo-search")
    elif research_button and not research_query:
        st.warning("⚠️ Ingresa un término de investigación")

# TAB 5: REPORTS  
with tab5:
    st.header("📊 Informes y Evidencia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Generar Informe")
        
        report_topic = st.text_input(
            "📋 Tema del informe:",
            placeholder="Ej: Estado de compliance EU-GMP"
        )
        
        report_data = st.text_area(
            "📄 Datos adicionales (opcional):",
            height=100,
            placeholder="Información adicional para el informe..."
        )
        
        if st.button("📊 Generar Informe Completo"):
            if report_topic:
                # Auto-investigar si no hay datos
                if not report_data and FEATURES["websearch"]:
                    with st.spinner("📖 Recopilando información..."):
                        report_data = safe_web_research(report_topic, 5)
                
                # Generar informe
                with st.spinner("📝 Generando informe..."):
                    report = generate_report(report_topic, report_data or "Información base disponible", agent)
                    st.markdown(report)
                    
                    # Botón de descarga
                    filename = f"informe_{report_topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                    st.download_button(
                        label="💾 Descargar Informe",
                        data=report,
                        file_name=filename,
                        mime="text/markdown",
                        use_container_width=True
                    )
            else:
                st.warning("⚠️ Ingresa un tema para el informe")
    
    with col2:
        st.subheader("📝 Log de Evidencia")
        
        evidence_df = load_evidence_log()
        
        if not evidence_df.empty:
            # Mostrar estadísticas
            st.metric("Total de consultas", len(evidence_df))
            
            # Filtros
            agent_filter = st.selectbox("Filtrar por agente:", ["Todos"] + list(AGENT_CONFIGS.keys()))
            
            # Aplicar filtro
            if agent_filter != "Todos":
                filtered_df = evidence_df[evidence_df["agent"] == agent_filter]
            else:
                filtered_df = evidence_df
            
            # Mostrar tabla
            st.dataframe(
                filtered_df[["timestamp", "agent", "action", "query"]].tail(20),
                use_container_width=True
            )
            
            # Opción de descarga
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "💾 Descargar Log CSV",
                csv_data,
                f"evidence_log_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.info("📋 No hay evidencia registrada aún")

# === FOOTER ===
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("🌿 **Green Hill Cockpit Multimedia**")

with footer_col2:
    st.markdown(f"🔗 LangGraph: {connection_status}")

with footer_col3:
    st.markdown("⚡ *Powered by AI & LangGraph*")
