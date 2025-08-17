from __future__ import annotations
import os, io, json, uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st, pandas as pd
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pypdf import PdfReader
from docx import Document as DocxDocument

APP_TITLE = "🌿 Green Hill — Agent Console"
PERSIST_DIR = Path(".chroma").as_posix()
COLLECTION = "greenhill"
MODEL_NAME = "all-MiniLM-L6-v2"
EVIDENCE_FILE = Path("evidence.jsonl")
STATE_FILE = Path("state.json")

def now_iso(): return datetime.utcnow().isoformat(timespec="seconds")+"Z"
def append_evidence(rec: Dict[str,Any]):
    rec = {"ts": now_iso(), **rec}
    with EVIDENCE_FILE.open("a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False)+"\n")

def load_state():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception: pass
    state = {
        "phase": "Phase I — Pilot & Shadow Mode",
        "approver": "CEO",
        "command_priority": "user_first",
        "last_actions": [],
        "pending_approvals": [],
        "key_dates": {"zec_filing":"", "gmp_dossier":"", "cash_buffer_to":""}
    }
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state

def save_state(s:dict): STATE_FILE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
def log_action(event:str, payload:dict=None):
    s = st.session_state.get("_gh_state") or load_state()
    rec = {"ts": now_iso(), "event": event}
    if payload: rec.update(payload)
    s.setdefault("last_actions", []); s["last_actions"]=(s["last_actions"]+[rec])[-50:]
    st.session_state["_gh_state"]=s; save_state(s)

def read_file_to_text(name:str, b:bytes)->str:
    suf = Path(name).suffix.lower()
    try:
        if suf in {".txt",".md"}: return b.decode("utf-8","ignore")
        if suf == ".pdf":
            r = PdfReader(io.BytesIO(b)); return "\n\n".join([(p.extract_text() or "") for p in r.pages])
        if suf == ".docx":
            d = DocxDocument(io.BytesIO(b)); return "\n".join([p.text for p in d.paragraphs])
        return b.decode("utf-8","ignore")
    except Exception as e: return f"[Parse error for {name}: {e}]"

def chunk_text(t:str, size:int=1000, overlap:int=200)->List[str]:
    t=t.replace("\r","\n"); n=len(t); i=0; out=[]
    while i<n:
        j=min(i+size,n); c=t[i:j].strip()
        if c: out.append(c)
        i = j-overlap; 
        if i<0: i=0
        if i>=n: break
    return out

@st.cache_resource(show_spinner=False)
def get_collection():
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    embed = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    return client.get_or_create_collection(name=COLLECTION, embedding_function=embed, metadata={"hnsw:space":"cosine"})

st.set_page_config(page_title="Green Hill Agent Console", layout="wide")
st.title(APP_TITLE)
st.session_state["_gh_state"] = load_state()
GH = st.session_state["_gh_state"]

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Dashboard","Memory / Training","Search","Approvals","Evidence","Settings"], index=0)
    st.markdown("---"); st.caption("Mode: Shadow · Approver: CEO · Network: OFF")

coll = get_collection()

if page=="Dashboard":
    c1,c2,c3,c4=st.columns(4)
    try: count=coll.count()
    except: count="—"
    c1.metric("Knowledge Chunks", count)
    c2.metric("Approvals (pending)", len(GH.get("pending_approvals",[])))
    c3.metric("Evidence bytes", EVIDENCE_FILE.stat().st_size if EVIDENCE_FILE.exists() else 0)
    c4.metric("Chroma Path", PERSIST_DIR)
    st.caption(f"Phase: {GH.get('phase','?')} · Approver: {GH.get('approver','CEO')}")
    st.markdown("### Recent actions")
    r=GH.get("last_actions", [])[-3:]
    if r:
        for x in reversed(r): st.write(f"• {x.get('ts')} — {x.get('event')} — { {k:v for k,v in x.items() if k not in ['ts','event']} }")
    else: st.write("No actions yet.")

elif page=="Memory / Training":
    st.subheader("Upload → Knowledge Vault (local)")
    files = st.file_uploader("PDF, DOCX, TXT, MD", type=["pdf","docx","txt","md"], accept_multiple_files=True)
    if files and st.button("Ingest to Vault", type="primary"):
        added=0
        for f in files:
            txt=read_file_to_text(f.name, f.read()); chunks=chunk_text(txt)
            ids=[f"{Path(f.name).name}:{i}:{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
            metas=[{"file":f.name,"idx":i,"ingested_at":now_iso()} for i in range(len(chunks))]
            if chunks: coll.add(ids=ids, documents=chunks, metadatas=metas); added+=len(chunks)
        append_evidence({"event":"ingest","files":[f.name for f in files],"chunks":added})
        log_action("ingest", {"files":[f.name for f in files], "chunks":added})
        st.success(f"Ingested {added} chunks.")

elif page=="Search":
    st.subheader("Retrieve (local, with citations)")
    q = st.text_input("Ask/search")
    k = st.slider("Top results",1,10,5)
    if st.button("Search", type="primary") and q:
        res = coll.query(query_texts=[q], n_results=k)
        append_evidence({"event":"search","query":q,"n_results":k})
        log_action("search", {"query":q, "n_results":k})
        docs = res.get("documents",[[]])[0]; metas=res.get("metadatas",[[]])[0]; ids=res.get("ids",[[]])[0]
        for i,(doc,meta,_id) in enumerate(zip(docs,metas,ids), start=1):
            with st.expander(f"#{i} • {_id} • {meta.get('file','?')} • idx={meta.get('idx','?')}"):
                st.write(doc); st.caption(f"Source: {meta}")

elif page=="Approvals":
    st.subheader("Approvals queue (persistent)")
    if "approvals" not in st.session_state: st.session_state.approvals=[]
    with st.form("add_approval"):
        title=st.text_input("Title","Codex run: baseline stable")
        link=st.text_input("Evidence link (optional)","")
        if st.form_submit_button("Add"):
            item={"id":uuid.uuid4().hex[:8],"title":title,"link":link,"at":now_iso(),"status":"Pending"}
            st.session_state.approvals.append(item)
            GH.setdefault("pending_approvals",[]).append(item); save_state(GH)
            append_evidence({"event":"approval_added", **item}); log_action("approve_add", {"id":item["id"],"title":item["title"]})
            st.success("Added.")
    if st.session_state.approvals:
        df=pd.DataFrame(st.session_state.approvals); st.dataframe(df, use_container_width=True)
    st.caption(f"Pending approvals (persistent): {len(GH.get('pending_approvals',[]))}")

elif page=="Evidence":
    st.subheader("Evidence Locker (local JSONL)")
    if EVIDENCE_FILE.exists():
        lines=EVIDENCE_FILE.read_text(encoding="utf-8").splitlines()
        st.caption(f"Entries: {len(lines)} • File: {EVIDENCE_FILE}")
        for i,line in enumerate(lines[-200:], start=max(1,len(lines)-199)):
            try: rec=json.loads(line)
            except: rec={"raw":line}
            with st.expander(f"Entry {i}: {rec.get('event','?')} @ {rec.get('ts','?')}"):
                st.json(rec)
        st.download_button("Download evidence.jsonl", data=EVIDENCE_FILE.read_bytes(), file_name="evidence.jsonl")
    else: st.info("No evidence yet. Ingest or search to create entries.")

elif page=="Settings":
    st.subheader("Settings")
    st.write("Chroma path:", PERSIST_DIR); st.write("Collection:", COLLECTION); st.write("Embedding model:", MODEL_NAME)
    with st.expander("Key dates (persistent)"):
        ks=GH.get("key_dates",{})
        z=st.text_input("ZEC filing (YYYY-MM-DD)", ks.get("zec_filing",""))
        g=st.text_input("GMP dossier (YYYY-MM-DD)", ks.get("gmp_dossier",""))
        c=st.text_input("Cash buffer to", ks.get("cash_buffer_to",""))
        if st.button("Save key dates"):
            GH["key_dates"]={"zec_filing":z,"gmp_dossier":g,"cash_buffer_to":c}; save_state(GH); st.success("Saved."); log_action("key_dates_update", GH["key_dates"])
st.markdown("---"); st.caption("Shadow-mode · Single approver · Local evidence logging")
