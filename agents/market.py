"""Market Agent - Market analysis and competitive intelligence"""
import os
from typing import Dict, Any, Optional
from openai import OpenAI

def run_market(question: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Market agent implementation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"answer": "OPENAI_API_KEY not configured", "meta": {"agent": "market", "tokens": 0}}
    
    client = OpenAI(api_key=api_key)
    context = "You are the Market Intelligence Agent for Green Hill Canarias. Analyze markets, competitors, and opportunities."
    
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
            "meta": {"agent": "market", "tokens": response.usage.total_tokens}
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": {"agent": "market", "tokens": 0}}
