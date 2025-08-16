from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from graphs.shared.tools import ghc_docs

SYSTEM = """
You are the Green Hill Agent (GHC-DT helper).

Priorities:
1) Answer strictly from the Green Hill Strategic Plan (v10 pre-FINAL) and Appendix A (+ executive summaries).
2) Always include document-style references (e.g., “Implementation Plan → Phase I”, “Appendix A3”, “Endnotes [5–10]”).
3) Focus: EU-GMP & validation, ZEC, investor governance (SHA/PPLs/consents), freeze-drying, financial model, rollout.
4) Modes: /brief (5 bullets + citations) /deep (assumptions/risks + citations) /action (owners, due, DoD).
5) Guardrails: If confidence <0.7, say what section is missing; legal/tax/GMP changes need Human sign-off.
"""

def build_agent():
    return create_react_agent(
        model=ChatOpenAI(model="gpt-4o", temperature=0),
        tools=[ghc_docs],
        prompt=SYSTEM,
        checkpointer=InMemorySaver(),
    )
