"""Legacy shim exposing the LangGraph app build utilities."""
from app.ghc_twin import (
    build_graph,
    digital_twin,
    intake_node,
    classify_request,
    router,
    app,
)

__all__ = [
    "build_graph",
    "digital_twin",
    "intake_node",
    "classify_request",
    "router",
    "app",
]
