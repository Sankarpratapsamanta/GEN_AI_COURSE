from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import (StateGraph,START,END)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition



llm = ChatGroq(
    model = "model_name",
    temperature=0,
)


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

@tool
def get_employee_count():
    """Return the current number of employees in the company"""

    return "The Company currently has 200 employees"


tools=[
    get_employee_count
]

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages":[response]
    }


tool_node = ToolNode(tools)

builder = StateGraph(AgentState)

builder.add_node("chatbot",chatbot)
builder.add_node("tools",tool_node)


builder.add_edge(START,"chatbot")

builder.add_conditional_edges("chatbot",tools_condition)

builder.add_edge("tools","chatbot")

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({
        "messages":[
            {
                "role":"user",
                "content":"How many employees does the company have?"
            }
        ]
    })

    for message in result["messages"]:
        print(message.content)