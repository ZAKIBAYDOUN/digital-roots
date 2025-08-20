"""Risk Agent - Risk assessment and mitigation"""
import os
from typing import Dict, Any, Optional
from openai import OpenAI

def run_risk(question: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Risk agent implementation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"answer": "OPENAI_API_KEY not configured", "meta": {"agent": "risk", "tokens": 0}}
    
    client = OpenAI(api_key=api_key)
    context = "You are the Risk Management Agent for Green Hill Canarias. Identify, assess, and mitigate risks."
    
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
            "meta": {"agent": "risk", "tokens": response.usage.total_tokens}
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": {"agent": "risk", "tokens": 0}}
