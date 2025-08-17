from pathlib import Path
import uuid
import json
from datetime import datetime

import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PERSIST_DIR = Path(".chroma").as_posix()
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "greenhill"
STATE_FILE = Path("state.json")

DEFAULT_STATE = {
    "command_priority": "user_first",
    "last_tasks": [],
    "approver": "CEO",
    "mode": "shadow",
}


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    save_state(DEFAULT_STATE)
    return DEFAULT_STATE.copy()


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


state = load_state()

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


def log_action(action: str, detail: str):
    record = {
        "action": action,
        "detail": detail,
        "ts": datetime.utcnow().isoformat(),
    }
    state.setdefault("last_tasks", []).append(record)
    save_state(state)

st.set_page_config(page_title="Green Hill Corpus Hub", page_icon="📚")
st.title("Green Hill Corpus Hub")

text = st.text_area("Enter text to ingest")
if st.button("Ingest text"):
    if text.strip():
        coll.add(documents=[text], ids=[str(uuid.uuid4())])
        log_action("ingest_text", text[:50])
        st.success("Ingested")
    else:
        st.warning("No text provided")

uploaded_files = st.file_uploader("Upload text files", accept_multiple_files=True, type=["txt", "md"])
if st.button("Ingest files") and uploaded_files:
    for file in uploaded_files:
        content = file.read().decode("utf-8", errors="ignore")
        coll.add(
            documents=[content],
            ids=[str(uuid.uuid4())],
            metadatas=[{"source": file.name}],
        )
        log_action("ingest_file", file.name)
    st.success("Files ingested")


query = st.text_input("Search corpus")
if st.button("Search") and query:
    res = coll.query(query_texts=[query], n_results=3)
    docs = res.get("documents", [[]])[0]
    for d in docs:
        st.write(d)
    log_action("search", query)
