"""Compliance Agent - Regulatory compliance and quality assurance"""
import os
from typing import Dict, Any, Optional
from openai import OpenAI

def run_compliance(question: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compliance/QA agent implementation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"answer": "OPENAI_API_KEY not configured", "meta": {"agent": "compliance", "tokens": 0}}
    
    client = OpenAI(api_key=api_key)
    context = "You are the Compliance & QA Agent for Green Hill Canarias. Ensure regulatory compliance and quality."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ]
        )
        return {
            "answer": response.choices[0].message.content,
            "meta": {"agent": "compliance", "tokens": response.usage.total_tokens}
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": {"agent": "compliance", "tokens": 0}}
