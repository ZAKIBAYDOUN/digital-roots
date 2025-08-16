# app/ghc_twin.py
import os
from typing import List
from langgraph.graph import StateGraph, START, END
from app.models import TwinState, AgentName, Message
from app.document_store import get_document_store
from app.agents import (
    strategy_node,
    finance_node,
    operations_node,
    market_intel_node as market_node,
    risk_node,
    compliance_node,
    innovation_node,
    green_hill_node,
    finalize_node,
)


def classify_request(state: TwinState) -> List[AgentName]:
    # Simple role-based classification; extend with keywords as needed
    st = (state.source_type or "public").lower()
    if st == "master":
        return [
            AgentName.STRATEGY,
            AgentName.FINANCE,
            AgentName.OPERATIONS,
            AgentName.MARKET,
            AgentName.RISK,
            AgentName.COMPLIANCE,
            AgentName.INNOVATION,
            AgentName.GREEN_HILL,
        ]
    if st in {"shareholder", "investor"}:
        return [
            AgentName.STRATEGY,
            AgentName.FINANCE,
            AgentName.MARKET,
            AgentName.RISK,
            AgentName.GREEN_HILL,
        ]
    if st in {"supplier", "provider"}:
        return [AgentName.OPERATIONS, AgentName.COMPLIANCE]
    if st == "public":
        return [AgentName.MARKET, AgentName.STRATEGY]
    if st == "ocs_feed":
        return [AgentName.OPERATIONS, AgentName.COMPLIANCE]
    if st == "web_source":
        return [AgentName.MARKET, AgentName.RISK]
    return []


def digital_twin(state: TwinState) -> TwinState:
    # Validate input
    if not state.question:
        state.finalize = True
        state.final_answer = (
            'Error: Missing "question". Send {"question": "..."} along with source_type.'
        )
        return state

    # Load vector store and attach context
    persist_dir = (
        os.getenv("VECTORSTORE_DIR")
        or os.getenv("VECTOR_STORE_DIR")
        or "vector_store"
    )
    store = get_document_store(persist_dir)
    if store and store.is_available():
        ctx = store.query(state.question, k=5)
        state.context["retrieved_docs"] = ctx.split("\n\n") if ctx else []
    else:
        state.context["retrieved_docs"] = ["No vector store available"]

    # Classify
    # Allow direct mode via target_agent/target_agents
    if state.target_agent and state.target_agent not in state.target_agents:
        state.target_agents.append(state.target_agent)
    targets = state.target_agents or classify_request(state)
    state.target_agents = targets
    if not targets:
        state.finalize = True
        state.final_answer = (
            "No suitable agents selected. Provide a clearer source_type or question."
        )
        return state

    # First hop
    state.next_agent = targets[0]
    return state


def intake_node(state: TwinState) -> TwinState:
    """Accepts arbitrary document/feed input and does light classification.

    - If payload_ref present and no question: prioritize innovation/operations.
    - If web_source: market and risk.
    - If ocs_feed: operations and compliance.
    """
    st = state
    st.history.append(Message(role="system", content="Intake processed"))
    targets = st.target_agents or []
    stype = (st.source_type or "public").lower()
    if st.payload_ref and not st.question:
        if AgentName.INNOVATION not in targets:
            targets.append(AgentName.INNOVATION)
        if AgentName.OPERATIONS not in targets:
            targets.append(AgentName.OPERATIONS)
    elif stype == "web_source":
        targets = targets or [AgentName.MARKET, AgentName.RISK]
    elif stype == "ocs_feed":
        targets = targets or [AgentName.OPERATIONS, AgentName.COMPLIANCE]
    st.target_agents = targets
    # If no question, allow flow to digital_twin which will fetch context & route
    return st


def router(state):
    # Accept both dict and TwinState
    st = state if isinstance(state, TwinState) else TwinState(**state)
    if st.finalize:
        return END
    m = {
        AgentName.STRATEGY: AgentName.STRATEGY.value,
        AgentName.FINANCE: AgentName.FINANCE.value,
        AgentName.OPERATIONS: AgentName.OPERATIONS.value,
        AgentName.MARKET: AgentName.MARKET.value,
        AgentName.RISK: AgentName.RISK.value,
        AgentName.COMPLIANCE: AgentName.COMPLIANCE.value,
        AgentName.INNOVATION: AgentName.INNOVATION.value,
        AgentName.GREEN_HILL: AgentName.GREEN_HILL.value,
    }
    # If no explicit next agent but not finalized, go to finalize node
    if st.next_agent is None and not st.finalize:
        return "finalize"
    return m.get(st.next_agent, END)


def build_graph():
    g = StateGraph(TwinState)
    # Initialize a single document store instance
    persist_dir = (
        os.getenv("VECTORSTORE_DIR")
        or os.getenv("VECTOR_STORE_DIR")
        or "vector_store"
    )
    store = get_document_store(persist_dir)
    # Wrappers to convert dict<->TwinState for nodes
    def wrap(node_fn):
        def _wrapped(s):
            st = s if isinstance(s, TwinState) else TwinState(**s)
            out = node_fn(st)
            return out.model_dump() if isinstance(out, TwinState) else out
        return _wrapped
    def wrap_with_store(node_fn):
        def _wrapped(s):
            st = s if isinstance(s, TwinState) else TwinState(**s)
            out = node_fn(st, store)
            return out.model_dump() if isinstance(out, TwinState) else out
        return _wrapped
    # Nodes
    g.add_node("intake", wrap(intake_node))
    g.add_node("digital_twin", wrap(digital_twin))
    g.add_node(AgentName.STRATEGY.value, wrap_with_store(strategy_node))
    g.add_node(AgentName.FINANCE.value, wrap_with_store(finance_node))
    g.add_node(AgentName.OPERATIONS.value, wrap_with_store(operations_node))
    g.add_node(AgentName.MARKET.value, wrap_with_store(market_node))
    g.add_node(AgentName.RISK.value, wrap_with_store(risk_node))
    g.add_node(AgentName.COMPLIANCE.value, wrap_with_store(compliance_node))
    g.add_node(AgentName.INNOVATION.value, wrap_with_store(innovation_node))
    g.add_node(AgentName.GREEN_HILL.value, wrap_with_store(green_hill_node))
    g.add_node("finalize", wrap_with_store(finalize_node))

    # Edges
    g.add_edge(START, "intake")
    g.add_edge("intake", "digital_twin")
    route_map = {
        AgentName.STRATEGY.value: AgentName.STRATEGY.value,
        AgentName.FINANCE.value: AgentName.FINANCE.value,
        AgentName.OPERATIONS.value: AgentName.OPERATIONS.value,
        AgentName.MARKET.value: AgentName.MARKET.value,
        AgentName.RISK.value: AgentName.RISK.value,
        AgentName.COMPLIANCE.value: AgentName.COMPLIANCE.value,
        AgentName.INNOVATION.value: AgentName.INNOVATION.value,
        AgentName.GREEN_HILL.value: AgentName.GREEN_HILL.value,
        "finalize": "finalize",
        END: END,
    }
    g.add_conditional_edges("digital_twin", router, route_map)
    for agent in [
        AgentName.STRATEGY,
        AgentName.FINANCE,
        AgentName.OPERATIONS,
        AgentName.MARKET,
        AgentName.RISK,
        AgentName.COMPLIANCE,
        AgentName.INNOVATION,
        AgentName.GREEN_HILL,
    ]:
        g.add_conditional_edges(agent.value, router, route_map)

    return g.compile()
app = build_graph()
