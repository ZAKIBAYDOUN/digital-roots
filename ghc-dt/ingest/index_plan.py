import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not found. Please set before ingestion.")

PLAN_DATA_DIR = os.getenv("PLAN_DATA_DIR", "data")
DOCS = [f for f in os.listdir(PLAN_DATA_DIR) if f.endswith((".pdf", ".docx"))]

docs = []
for f in DOCS:
    path = os.path.join(PLAN_DATA_DIR, f)
    docs += (PyPDFLoader(path).load() if f.endswith(".pdf") else Docx2txtLoader(path).load())

# Split documents and embed with OpenAI
splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150).split_documents(docs)
embed = OpenAIEmbeddings(model="text-embedding-3-small")
vs = FAISS.from_documents(splits, embed)
base_dir = Path(__file__).resolve().parent.parent
vs_dir = base_dir / "graphs" / "shared" / "vectorstore"
vs.save_local(str(vs_dir))
print(f"Indexed → {vs_dir}  (files: {len(DOCS)})")
