"""Legacy shim for launching the Digital Twin app."""
from app.main import app, run_query, create_app


def create_simple_graph():
    """Backwards-compatible wrapper returning the LangGraph app."""
    return create_app()


def create_multi_agent_graph():
    """Alias to ``create_app`` for legacy imports."""
    return create_app()


__all__ = [
    "app",
    "run_query",
    "create_simple_graph",
    "create_multi_agent_graph",
]
