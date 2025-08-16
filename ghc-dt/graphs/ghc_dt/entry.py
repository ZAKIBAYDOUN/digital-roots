from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, List, Dict, Any
from graphs.ghc_dt.agent import build_agent

class S(TypedDict):
    messages: List[Dict[str, Any]]

def _node(state: S):
    agent = build_agent()
    res = agent.invoke(state)
    return {"messages": res["messages"] if "messages" in res else res}

graph = StateGraph(S)
graph.add_node("ghc_dt", _node)
graph.add_edge(START, "ghc_dt")
graph = graph.compile(checkpointer=InMemorySaver())
