import streamlit as st
from langgraph_sdk import get_sync_client

st.set_page_config(page_title="GHC-DT Control Room", layout="wide")

BASE = st.sidebar.selectbox("Deployment", [
    "https://digital-roots-f97ac74784c6517184d8a7c3bbca5459.us.langgraph.app",   # Lab
    "https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app"      # Prod
])
API_KEY = st.secrets["LANGSMITH_API_KEY"]
client = get_sync_client(url=BASE, api_key=API_KEY)

st.title("Green Hill CEO Digital Twin (GHC-DT)")
msg = st.text_area("Message", "/brief Summarize EU-GMP readiness with citations.")
if st.button("Run"):
    a = client.assistants.search(graph_id="ghc_dt", limit=1)[0]
    t = client.threads.create(metadata={"audience":"internal"})
    with st.status("Streaming…"):
        for ev in client.runs.stream(
            thread_id=t["thread_id"],
            assistant_id=a["assistant_id"],
            input={"messages":[{"role":"user","content": msg}]},
            stream_mode=["messages","updates"]
        ):
            if ev["event"]=="messages/response.delta":
                st.write(ev["data"]["delta"])
