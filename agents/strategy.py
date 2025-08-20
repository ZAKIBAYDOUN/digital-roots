"""Strategy Agent - Strategic planning and business model analysis"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from openai import OpenAI

def run_strategy(question: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Strategy agent implementation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "answer": "OPENAI_API_KEY not configured",
            "meta": {"agent": "strategy", "tokens": 0}
        }
    
    client = OpenAI(api_key=api_key)
    state = state or {}
    
    context = f"""You are the Strategy Agent for Green Hill Canarias.
Current phase: {state.get('phase', 'Phase 1')}
Provide strategic insights and planning guidance."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ]
        )
        return {
            "answer": response.choices[0].message.content,
            "meta": {"agent": "strategy", "tokens": response.usage.total_tokens}
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": {"agent": "strategy", "tokens": 0}}
