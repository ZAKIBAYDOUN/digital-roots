"""Simple smoke test for running the Green Hill Canarias twin."""

import os


def main() -> None:
    """Run a basic invocation against the twin."""
    # Ensure no real API key is used during smoke testing
    os.environ.pop("OPENAI_API_KEY", None)

    from app.ghc_twin import app

    state = {
        "question": "What are the investor priorities for Green Hill Canarias?",
        "source_type": "investor",
    }

    res = app.invoke(state)
    print(
        {
            "finalize": res.get("finalize"),
            "final_answer_len": len(res.get("final_answer", "") or ""),
            "has_strategy": bool(res.get("strategy_output")),
            "has_finance": bool(res.get("finance_output")),
            "has_market": bool(res.get("market_output")),
            "has_risk": bool(res.get("risk_output")),
            "has_green_hill_memo": bool(res.get("green_hill_response")),
        }
    )


if __name__ == "__main__":
    main()
