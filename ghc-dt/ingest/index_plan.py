import os, glob
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

DATA_DIR = os.getenv("PLAN_DATA_DIR", "data")

def discover_docs():
    patterns = ["*.pdf", "*.docx", "*.doc"]
    files = []
    for pat in patterns:
        files += glob.glob(os.path.join(DATA_DIR, pat))
    if not files:
        raise SystemExit(f"No plan files found in {DATA_DIR}/ — copy Strategic Plan, Appendix A, exec summaries, SHA there.")
    return files

def load_docs(paths):
    docs=[]
    for p in paths:
        if p.lower().endswith(".pdf"):
            docs += PyPDFLoader(p).load()
        else:
            docs += Docx2txtLoader(p).load()
    return docs

def split_docs(docs):
    return RecursiveCharacterTextSplitter(chunk_size=1100, chunk_overlap=150).split_documents(docs)

if __name__ == "__main__":
    assert os.environ.get("OPENAI_API_KEY"), "Set OPENAI_API_KEY"
    files = discover_docs()
    docs = load_docs(files)
    chunks = split_docs(docs)
    vs = FAISS.from_documents(chunks, OpenAIEmbeddings())
    vs.save_local("vectorstore")
    print(f"Indexed → ./vectorstore  (files: {len(files)})")
