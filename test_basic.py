#!/usr/bin/env python3
"""
Basic test for the app without heavy dependencies
"""
import os
import sys

from app.models import TwinState, AgentName, Message
from test_mock_app import app


def test_minimal_invoke_investor():
    state = TwinState(question="What is the ROI for EU-GMP compliance?", source_type="investor")
    result = app.invoke(state)
    assert result["finalize"] is True
    assert result.get("final_answer")


def test_agent_enums_values():
    assert AgentName.STRATEGY.value == "strategy"
    assert AgentName.FINANCE.value == "finance"
    assert AgentName.OPERATIONS.value == "operations"
    assert AgentName.MARKET.value == "market"
    assert AgentName.RISK.value == "risk"
    assert AgentName.COMPLIANCE.value == "compliance"
    assert AgentName.INNOVATION.value == "innovation"
    assert AgentName.GREEN_HILL.value == "green_hill_gpt"


if __name__ == "__main__":
    # Simple runner
    try:
        test_minimal_invoke_investor()
        test_agent_enums_values()
        print("OK")
        sys.exit(0)
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)