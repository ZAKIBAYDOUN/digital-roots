from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from graphs.shared.tools import ghc_docs

SYSTEM = open("config/ghc_dt_system_prompt.txt").read()
DEV = open("config/ghc_dt_developer_prompt.txt").read()

def build_agent():
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    return create_react_agent(
        model=model,
        tools=[ghc_docs],
        prompt=SYSTEM + "\n\n[Developer]\n" + DEV,
    )
