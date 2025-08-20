"""Code Agent - Engineering and technical support"""
import os
from typing import Dict, Any, Optional
from openai import OpenAI

def run_code(question: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Code/engineering agent implementation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"answer": "OPENAI_API_KEY not configured", "meta": {"agent": "code", "tokens": 0}}
    
    client = OpenAI(api_key=api_key)
    context = "You are the Code Engineering Agent for Green Hill Canarias. Provide technical guidance and code solutions."
    
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
            "meta": {"agent": "code", "tokens": response.usage.total_tokens}
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": {"agent": "code", "tokens": 0}}
