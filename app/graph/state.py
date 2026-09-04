from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CompanyAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id:str
    user_role:str
    long_term_memory:list[str]
    security_error:str | None
    blocked_tool_call_id:str | None