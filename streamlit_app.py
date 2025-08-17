import streamlit as st
import json, os
from datetime import datetime
import pandas as pd

STATE_FILE = "state.json"
LOG_FILE = "evidence.jsonl"

def run_command(query: str, mode: str, agent: str):
    return {
        "answer": f"[{agent}] {mode} → {query or '(no query)'}",
        "refs": []
    }

def get_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {
        "phase": "Phase I — Pilot & Shadow Mode",
        "zec_rate": 4.0,
        "cash_buffer_to": "",
        "key_dates": {"zec_filing": "", "gmp_dossier": "", "cash_buffer_to": ""}
    }

def set_state(key, value):
    state = get_state()
    state[key] = value
    json.dump(state, open(STATE_FILE, "w"), indent=2)
    return True

def get_log():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["timestamp","agent","action","query","answer","refs"])
    rows = []
    for line in open(LOG_FILE):
        try: rows.append(json.loads(line))
        except: continue
    return pd.DataFrame(rows)

def append_log(entry: dict):
    with open(LOG_FILE,"a") as f: f.write(json.dumps(entry)+"\n")

st.set_page_config(page_title="🌿 Green Hill Cockpit", layout="wide")

st.sidebar.title("⚙️ Control Panel")
mode = st.sidebar.radio("Command", ["/brief","/deep","/action","/sync","/evidence","/console"])
agent = st.sidebar.selectbox("Target Agent", ["CEO-DT","FP&A","QA/Validation","Governance"])

st.sidebar.subheader("Variables")
state = get_state()
phase = st.sidebar.text_input("Phase", state.get("phase",""))
zec = st.sidebar.number_input("ZEC Rate (%)", value=float(state.get("zec_rate",4.0)))
cash_buffer = st.sidebar.text_input("Cash Buffer", state.get("cash_buffer_to",""))
key_dates = state.get("key_dates",{})
key_dates["zec_filing"] = st.sidebar.text_input("ZEC Filing", key_dates.get("zec_filing",""))
key_dates["gmp_dossier"] = st.sidebar.text_input("GMP Dossier", key_dates.get("gmp_dossier",""))
key_dates["cash_buffer_to"] = st.sidebar.text_input("Cash Buffer To", key_dates.get("cash_buffer_to",""))

if st.sidebar.button("💾 Save Variables"):
    set_state("phase", phase)
    set_state("zec_rate", zec)
    set_state("cash_buffer_to", cash_buffer)
    set_state("key_dates", key_dates)
    st.sidebar.success("State updated")

tab1,tab2,tab3,tab4=st.tabs(["💬 Chat","📋 Actions","📑 Evidence Log","🏛 Governance"])

with tab1:
    st.header("Chat with Agents")
    if "history" not in st.session_state:
        st.session_state["history"] = []
    for turn in st.session_state["history"]:
        st.markdown(f"**You:** {turn['q']}")
        st.markdown(f"**{turn['agent']}:** {turn['a']}")
    q = st.text_input("Ask or instruct:")
    if st.button("Send"):
        resp = run_command(q, mode, agent)
        answer = resp["answer"] if isinstance(resp, dict) else str(resp)
        st.session_state["history"].append({"q": q, "a": answer, "agent": agent})
        append_log({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "action": mode,
            "query": q,
            "answer": answer,
            "refs": resp.get("refs",[]) if isinstance(resp, dict) else []
        })
        st.experimental_rerun()

with tab2:
    st.header("Tasks & Actions")
    resp = run_command("", "/action", agent)
    st.write(resp)

with tab3:
    st.header("Evidence Log")
    st.dataframe(get_log())

with tab4:
    st.header("Governance & State")
    st.json(get_state())
