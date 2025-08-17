"""
Mock langgraph implementation for testing
"""


class StateGraph:
    """Mock StateGraph class"""
    
    def __init__(self, state_type):
        self.state_type = state_type
    
    def add_node(self, name, func):
        pass
    
    def add_edge(self, from_node, to_node):
        pass
    
    def add_conditional_edges(self, node, router, mapping):
        pass
    
    def compile(self):
        return MockCompiledGraph()


class MockCompiledGraph:
    """Mock compiled graph that can invoke states"""
    
    def invoke(self, state):
        """Mock invoke that returns basic success"""
        from app.models import TwinState
        
        # Convert to TwinState if needed
        if isinstance(state, TwinState):
            result_state = state
        else:
            result_state = TwinState(**state)
        
        # Set the final state as successful
        result_state.finalize = True
        result_state.final_answer = f"Mock response to: {result_state.question or 'unknown'}"
        
        return result_state.model_dump()


# Mock constants
START = "START"
END = "END"