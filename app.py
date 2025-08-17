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


def load_state():
    if STATE_FILE.exists():
        with STATE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"logs": [], "pending": []}


def save_state(state):
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

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

state = load_state()

st.set_page_config(page_title="Green Hill Corpus Hub", page_icon="📚")
st.title("Green Hill Corpus Hub")

text = st.text_area("Enter text to ingest")
if st.button("Queue text"):
    if text.strip():
        item = {"id": str(uuid.uuid4()), "text": text, "metadata": {}}
        state["pending"].append(item)
        state["logs"].append(
            {"action": "ingest", "id": item["id"], "timestamp": datetime.utcnow().isoformat()}
        )
        save_state(state)
        st.success("Queued for approval")
    else:
        st.warning("No text provided")

uploaded_files = st.file_uploader(
    "Upload text files", accept_multiple_files=True, type=["txt", "md"]
)
if st.button("Queue files") and uploaded_files:
    for file in uploaded_files:
        content = file.read().decode("utf-8", errors="ignore")
        item = {
            "id": str(uuid.uuid4()),
            "text": content,
            "metadata": {"source": file.name},
        }
        state["pending"].append(item)
        state["logs"].append(
            {
                "action": "ingest",
                "id": item["id"],
                "source": file.name,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    save_state(state)
    st.success("Files queued for approval")

st.write(f"Pending ingestions: {len(state['pending'])}")
if state["pending"] and st.button("Approve pending ingestions"):
    for item in state["pending"]:
        coll.add(
            documents=[item["text"]],
            ids=[item["id"]],
            metadatas=[item["metadata"]],
        )
    state["logs"].append(
        {
            "action": "approve",
            "ids": [item["id"] for item in state["pending"]],
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    state["pending"] = []
    save_state(state)
    st.success("Pending ingestions approved")

query = st.text_input("Search query")
if st.button("Search") and query.strip():
    res = coll.query(query_texts=[query], n_results=5)
    docs = res.get("documents", [[]])[0]
    for doc in docs:
        st.write(doc)
    state["logs"].append(
        {"action": "search", "query": query, "timestamp": datetime.utcnow().isoformat()}
    )
    save_state(state)
