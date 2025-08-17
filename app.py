from pathlib import Path
import json
import uuid
from datetime import datetime

import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PERSIST_DIR = Path(".chroma").as_posix()
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "greenhill"

STATE_PATH = Path("state.json")
DEFAULT_STATE = {
    "command_priority": "user_first",
    "last_tasks": [],
    "approver": "CEO",
    "mode": "shadow",
}


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return DEFAULT_STATE.copy()


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2))


def record_action(action, **kwargs):
    state = st.session_state.setdefault("persistent_state", load_state())
    entry = {"action": action, "timestamp": datetime.utcnow().isoformat()}
    entry.update(kwargs)
    state.setdefault("last_tasks", []).append(entry)
    save_state(state)

@st.cache_resource(show_spinner=False)
def get_collection():
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    embed = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    return client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=embed,
        metadata={"hnsw:space": "cosine"},
    )

coll = get_collection()

st.set_page_config(page_title="Green Hill Corpus Hub", page_icon="📚")
st.title("Green Hill Corpus Hub")

state = st.session_state.setdefault("persistent_state", load_state())

with st.sidebar:
    st.header("State")
    st.json(state, expanded=False)

text = st.text_area("Enter text to ingest")
if st.button("Ingest text"):
    if text.strip():
        coll.add(documents=[text], ids=[str(uuid.uuid4())])
        st.success("Ingested")
        record_action("ingest_text")
    else:
        st.warning("No text provided")

uploaded_files = st.file_uploader(
    "Upload text files", accept_multiple_files=True, type=["txt", "md"]
)
if st.button("Ingest files") and uploaded_files:
    for file in uploaded_files:
        content = file.read().decode("utf-8", errors="ignore")
        coll.add(
            documents=[content],
            ids=[str(uuid.uuid4())],
            metadatas=[{"source": file.name}],
        )
        record_action("ingest_file", source=file.name)
    st.success("Files ingested")

query = st.text_input("Search corpus")
if st.button("Search corpus"):
    if query.strip():
        results = coll.query(query_texts=[query], n_results=5)
        st.session_state["search_results"] = results
        st.session_state["last_query"] = query
        record_action("search", query=query)
    else:
        st.warning("No query provided")

if "search_results" in st.session_state:
    st.subheader("Search Results")
    st.write(st.session_state["search_results"])
    if st.button("Approve search"):
        record_action("approval", query=st.session_state.get("last_query"))
        st.success("Approved")
