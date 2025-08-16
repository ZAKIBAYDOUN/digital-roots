from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class AgentName(str, Enum):
    """Canonical agent identifiers used throughout the app.

    Member names are uppercase while values are the lowercase identifiers
    referenced in tests and persisted data. The ``MARKET_INTEL`` alias is
    provided for backwards compatibility with older references to the market
    intelligence agent.
    """

    STRATEGY = "strategy"
    OPERATIONS = "operations"
    FINANCE = "finance"
    MARKET = "market"
    MARKET_INTEL = "market_intel"
    RISK = "risk"
    COMPLIANCE = "compliance"
    INNOVATION = "innovation"
    GREEN_HILL = "green_hill_gpt"


class Message(BaseModel):
    role: str
    content: str


class TwinState(BaseModel):
    # Who and what
    source_type: str = "public"  # master, shareholder, investor, supplier, provider, public, ocs_feed, web_source, media_upload
    source_id: Optional[str] = None
    origin: Optional[str] = None
    question: Optional[str] = None
    content_type: Optional[str] = None   # text, structured_data, binary, mixed
    payload_ref: Optional[str] = None
    priority: Optional[str] = "normal"
    timestamp: Optional[str] = None
    related_docs: List[str] = Field(default_factory=list)
    tone: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Context and history
    context: Dict[str, Any] = Field(default_factory=dict)
    history: List[Message] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

    # Agents’ outputs
    strategy_output: Optional[Dict[str, Any]] = None
    operations_output: Optional[Dict[str, Any]] = None
    finance_output: Optional[Dict[str, Any]] = None
    market_output: Optional[Dict[str, Any]] = None
    risk_output: Optional[Dict[str, Any]] = None
    compliance_output: Optional[Dict[str, Any]] = None
    innovation_output: Optional[Dict[str, Any]] = None
    green_hill_response: Optional[Dict[str, Any]] = None

    # Orchestration
    current_agent: Optional[AgentName] = None
    next_agent: Optional[AgentName] = None
    finalize: bool = False
    final_answer: Optional[str] = None
    errors: List[str] = Field(default_factory=list)

    # Optional: direct mode and multi-target scheduling
    target_agent: Optional[AgentName] = None
    target_agents: List[AgentName] = Field(default_factory=list)

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True
