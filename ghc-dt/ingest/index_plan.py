import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PLAN_DATA_DIR = os.getenv("PLAN_DATA_DIR", "data")
DOCS = [f for f in os.listdir(PLAN_DATA_DIR) if f.endswith((".pdf", ".docx"))]

docs = []
for f in DOCS:
    path = os.path.join(PLAN_DATA_DIR, f)
    docs += (PyPDFLoader(path).load() if f.endswith(".pdf") else Docx2txtLoader(path).load())

splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150).split_documents(docs)
embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vs = FAISS.from_documents(splits, embed)
vs.save_local("vectorstore")
print(f"Indexed → ./vectorstore  (files: {len(DOCS)})")
