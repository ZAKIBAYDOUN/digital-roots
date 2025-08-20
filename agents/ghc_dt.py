"""CEO Digital Twin (ghc_dt) - Executive orchestrator"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from openai import OpenAI

def run_ghc_dt(question: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """CEO Digital Twin orchestrator implementation"""
    # Get configuration
    model = os.getenv("GHC_DT_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("GHC_DT_TEMPERATURE", "0.2"))
    evidence_log = os.getenv("GHC_DT_EVIDENCE_LOG")
    
    # Get system prompt
    default_prompt = """You are GHC-DT, the CEO Digital Twin of Green Hill Canarias.
You orchestrate between agents and provide executive-level insights.
Your style is operational, rational, and focused on execution.
Current context: {context}"""
    
    system_prompt = os.getenv("GHC_DT_SYSTEM_PROMPT", default_prompt)
    
    # Initialize OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "answer": "OPENAI_API_KEY not configured",
            "meta": {"agent": "ghc_dt", "tokens": 0}
        }
    
    client = OpenAI(api_key=api_key)
    state = state or {}
    
    # Build context
    context = json.dumps({
        "phase": state.get("phase", "Phase 1"),
        "zec_rate": state.get("zec_rate", 4),
        "cash_buffer_to": state.get("cash_buffer_to", "2026-06-30")
    })
    
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt.format(context=context)},
                {"role": "user", "content": question}
            ]
        )
        
        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens
        
        # Log to evidence if configured
        if evidence_log:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "agent": "ghc_dt",
                "question": question,
                "answer": answer,
                "tokens": tokens
            }
            with open(evidence_log, "a") as f:
                f.write(json.dumps(entry) + "\n")
        
        return {"answer": answer, "meta": {"agent": "ghc_dt", "tokens": tokens}}
    
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": {"agent": "ghc_dt", "tokens": 0}}
