"""Finance Agent - FP&A and financial modeling"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from openai import OpenAI

def run_finance(question: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Finance FP&A agent implementation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "answer": "OPENAI_API_KEY not configured",
            "meta": {"agent": "finance", "tokens": 0}
        }
    
    client = OpenAI(api_key=api_key)
    state = state or {}
    
    context = f"""You are the Finance FP&A Agent for Green Hill Canarias.
ZEC tax rate: {state.get('zec_rate', 4)}%
Cash buffer target: {state.get('cash_buffer_to', '2026-06-30')}
Provide financial analysis and planning insights."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ]
        )
        return {
            "answer": response.choices[0].message.content,
            "meta": {"agent": "finance", "tokens": response.usage.total_tokens}
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": {"agent": "finance", "tokens": 0}}
