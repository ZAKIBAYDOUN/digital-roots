from pathlib import Path
import uuid
import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PERSIST_DIR = Path(".chroma").as_posix()
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "greenhill"

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

text = st.text_area("Enter text to ingest")
if st.button("Ingest text"):
    if text.strip():
        coll.add(documents=[text], ids=[str(uuid.uuid4())])
        st.success("Ingested")
    else:
        st.warning("No text provided")

uploaded_files = st.file_uploader("Upload text files", accept_multiple_files=True, type=["txt", "md"])
if st.button("Ingest files") and uploaded_files:
    for file in uploaded_files:
        content = file.read().decode("utf-8", errors="ignore")
        coll.add(documents=[content], ids=[str(uuid.uuid4())], metadatas=[{"source": file.name}])
    st.success("Files ingested")
