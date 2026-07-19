from langchain.agents import AgentState
from pydantic import EmailStr


class CustomAgentState(AgentState):
    mail: EmailStr
    name: str
