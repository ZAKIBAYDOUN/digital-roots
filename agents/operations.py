"""Operations Agent - Operational excellence and execution"""
import os
from typing import Dict, Any, Optional
from openai import OpenAI

def run_operations(question: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Operations agent implementation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"answer": "OPENAI_API_KEY not configured", "meta": {"agent": "operations", "tokens": 0}}
    
    client = OpenAI(api_key=api_key)
    context = "You are the Operations Agent for Green Hill Canarias. Focus on operational efficiency and execution."
    
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
            "meta": {"agent": "operations", "tokens": response.usage.total_tokens}
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": {"agent": "operations", "tokens": 0}}
