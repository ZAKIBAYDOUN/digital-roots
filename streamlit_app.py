import os
import json
import streamlit as st
from app.ghc_twin import app
from app.models import TwinState, AgentName

st.set_page_config(page_title="GHC Digital Twin Tester", page_icon="🧪", layout="wide")
st.title("Green Hill Canarias – Digital Twin Tester")
st.caption("Visual interface to run and debug the LangGraph app (ghc)")

with st.sidebar:
    st.header("Settings")
    default_question = st.text_input("Question", value="What is the 9-month plan for EU-GMP compliance and ROI >20%?")
    source_type = st.selectbox(
        "Source Type",
        options=["public","master","shareholder","investor","supplier","provider","ocs_feed","web_source","media_upload"],
        index=0,
    )
    payload_ref = st.text_input("Payload Ref (URL or ID)", value="")
    metadata_raw = st.text_area("Metadata (JSON)", value="{}", height=100)
    try:
        metadata = json.loads(metadata_raw) if metadata_raw.strip() else {}
    except Exception:
        metadata = {}
        st.warning("Invalid metadata JSON. Using empty dict.")
    # Optional targeting
    target = st.selectbox(
        "Target agent (optional)",
        options=["(auto)"] + [a.name for a in AgentName],
        index=0,
    )
    vector_dir = st.text_input(
        "VECTORSTORE_DIR",
        value=os.getenv("VECTORSTORE_DIR")
        or os.getenv("VECTOR_STORE_DIR")
        or "vector_store",
    )
    os.environ["VECTORSTORE_DIR"] = vector_dir
    run_button = st.button("Run Graph")
    st.markdown("---")
    st.caption("Tip: Leave question empty and set payload_ref to test content-only flow.")

col1, col2 = st.columns(2)

if run_button:
    st.subheader("Input")
    st.code(
        json.dumps(
            {
                "question": default_question,
                "source_type": source_type,
                "payload_ref": payload_ref or None,
                "metadata": metadata,
                "target_agent": None if target == "(auto)" else target,
            },
            ensure_ascii=False,
            indent=2,
        ),
        language="json",
    )

    try:
        # Build initial state (question may be empty; payload_ref/metadata allowed)
        init_state = TwinState(
            question=default_question.strip() or None,
            source_type=source_type,
            payload_ref=payload_ref.strip() or None,
            metadata=metadata,
            target_agent=(AgentName[target] if target != "(auto)" else None) if target else None,
        )
        result = app.invoke(init_state)

        with col1:
            st.subheader("Final Answer")
            st.write(result.get("final_answer"))
            st.subheader("Errors")
            errs = result.get("errors", [])
            if errs:
                for e in errs:
                    st.error(e)
            else:
                st.success("No errors")

        with col2:
            st.subheader("State Snapshot")
            st.json(result, expanded=False)
            st.subheader("Agent Outputs")
            for key in [
                "strategy_output","finance_output","operations_output",
                "market_output","risk_output","compliance_output","innovation_output"
            ]:
                if result.get(key) is not None:
                    with st.expander(key, expanded=False):
                        st.json(result.get(key), expanded=False)

    except Exception as e:
        st.exception(e)
        st.stop()

st.markdown("---")
st.caption("Use: `streamlit run streamlit_app.py` to launch locally. Configure OPENAI_API_KEY to enable vector store.")
