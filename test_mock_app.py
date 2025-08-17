"""
Simple mock app for testing without langgraph dependencies
"""
from app.models import TwinState, AgentName, Message


class MockApp:
    """Mock app for testing basic functionality"""
    
    def invoke(self, state):
        """Mock invoke method that returns a basic successful result"""
        if isinstance(state, TwinState):
            state_dict = state.model_dump()
        else:
            state_dict = state
            
        # Return a basic successful result
        return {
            "finalize": True,
            "final_answer": f"Mock response to: {state_dict.get('question', 'unknown')}",
            "question": state_dict.get("question"),
            "source_type": state_dict.get("source_type")
        }


# Create the mock app instance
app = MockApp()