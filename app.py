from pathlib import Path
import uuid
import json
from datetime import datetime
import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

STATE_FILE = Path("state.json")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    # default state
    state = {
        "phase": "Phase I — Pilot & Shadow Mode",
        "approver": "CEO",
        "command_priority": "user_first",
        "last_actions": [],
        "pending_approvals": [],
        "key_dates": {
            "zec_filing": "",
            "gmp_dossier": "",
            "cash_buffer_to": ""
        }
    }
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def log_action(event: str, payload: dict = None):
    s = st.session_state.get("_gh_state") or load_state()
    rec = {"ts": datetime.utcnow().isoformat(timespec="seconds") + "Z", "event": event}
    if payload:
        rec.update(payload)
    s.setdefault("last_actions", [])
    s["last_actions"] = (s["last_actions"] + [rec])[-50:]
    st.session_state["_gh_state"] = s
    save_state(s)

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

# Load persistent state once per session
st.session_state["_gh_state"] = load_state()
GH_STATE = st.session_state["_gh_state"]

page = st.sidebar.selectbox("Page", ["Dashboard", "Memory/Training", "Search", "Codex Runner", "Approvals", "Evidence", "Settings"])
st.title("Green Hill Corpus Hub")

if page == "Dashboard":
    st.caption(
        f"Phase: {st.session_state['_gh_state'].get('phase','?')}  ·  Approver: {st.session_state['_gh_state'].get('approver','CEO')}"
    )
    st.markdown("### Recent actions")
    recent = st.session_state["_gh_state"].get("last_actions", [])[-3:]
    if recent:
        for r in reversed(recent):
            st.write(
                f"• {r.get('ts','?')} — {r.get('event','?')} — { {k:v for k,v in r.items() if k not in ['ts','event']} }"
            )
    else:
        st.write("No actions yet.")

elif page == "Memory/Training":
    text = st.text_area("Enter text to ingest")
    if st.button("Ingest text"):
        if text.strip():
            coll.add(documents=[text], ids=[str(uuid.uuid4())])
            st.success("Ingested")
            log_action("ingest", {"files": [], "chunks": 1})
        else:
            st.warning("No text provided")

    uploaded_files = st.file_uploader(
        "Upload text files", accept_multiple_files=True, type=["txt", "md"]
    )
    if st.button("Ingest files") and uploaded_files:
        added = 0
        for file in uploaded_files:
            content = file.read().decode("utf-8", errors="ignore")
            coll.add(
                documents=[content],
                ids=[str(uuid.uuid4())],
                metadatas=[{"source": file.name}],
            )
            added += 1
        st.success("Files ingested")
        log_action("ingest", {"files": [f.name for f in uploaded_files], "chunks": added})

elif page == "Search":
    query = st.text_input("Search query")
    k = st.number_input("Results", min_value=1, max_value=20, value=5)
    if st.button("Search") and query.strip():
        res = coll.query(query_texts=[query], n_results=k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        for doc, meta in zip(docs, metas):
            st.write(f"{meta.get('source','')} — {doc[:200]}")
        log_action("search", {"query": query, "n_results": k})

elif page == "Codex Runner":
    st.write("Codex runner coming soon")

elif page == "Approvals":
    st.caption(
        f"Pending approvals (persistent): {len(st.session_state['_gh_state'].get('pending_approvals', []))}"
    )
    if "approvals" not in st.session_state:
        st.session_state.approvals = []
    title = st.text_input("Approval title")
    if st.button("Add approval") and title.strip():
        item = {"id": str(uuid.uuid4()), "title": title.strip()}
        st.session_state.approvals.append(item)
        s = st.session_state["_gh_state"]
        s.setdefault("pending_approvals", [])
        s["pending_approvals"].append(item)
        save_state(s)
        log_action("approve_add", {"id": item["id"], "title": item["title"]})
        st.success("Approval added")
    if st.session_state.approvals:
        st.markdown("### Session Approvals")
        for a in st.session_state.approvals:
            st.write(f"{a['id']} — {a['title']}")

elif page == "Evidence":
    st.write("Evidence viewer coming soon")

elif page == "Settings":
    with st.expander("Key dates (persistent)"):
        ks = st.session_state["_gh_state"].get("key_dates", {})
        zec = st.text_input("ZEC filing (YYYY-MM-DD)", ks.get("zec_filing", ""))
        gmp = st.text_input("GMP dossier (YYYY-MM-DD)", ks.get("gmp_dossier", ""))
        cash = st.text_input("Cash buffer to (e.g., 2026-Q4)", ks.get("cash_buffer_to", ""))
        if st.button("Save key dates"):
            s = st.session_state["_gh_state"]
            s["key_dates"] = {
                "zec_filing": zec,
                "gmp_dossier": gmp,
                "cash_buffer_to": cash,
            }
            save_state(s)
            st.success("Saved.")
            log_action("key_dates_update", s["key_dates"])
