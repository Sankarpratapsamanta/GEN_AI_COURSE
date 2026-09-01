from langgraph.graph import (StateGraph,START,END)

from langgraph.prebuilt import (ToolNode,tools_condition)
from app.graph.state import CompanyAgentState
from app.graph.nodes import (load_memory,create_agent_node,save_company_memory)
from app.tools.company_tools import (get_employee_count,get_company_location,get_working_hours)
from app.mcp_client.client import get_mcp_tools
from app.rag.retriever import search_company_documents
from app.graph.retry_tool import make_all_tools_retryable

async def create_company_graph(checkpointer):
    mcp_tools = (await get_mcp_tools())

    original_tools = [
        get_employee_count,
        get_company_location,
        get_working_hours,
        search_company_documents,
        *mcp_tools,
    ]

    tools = make_all_tools_retryable(original_tools)

    agent = create_agent_node(tools)

    tool_node = ToolNode(tools,handle_tool_errors=True)

    builder = StateGraph(CompanyAgentState)


    builder.add_node("load_memory",load_memory)
    builder.add_node("agent",agent)
    builder.add_node("tools",tool_node)
    builder.add_node("save_memory",save_company_memory)

    builder.add_edge(
        START,
        "load_memory",
    )

    builder.add_edge(
        "load_memory",
        "agent",
    )

    builder.add_conditional_edges("agent",tools_condition,{"tools":"tools","__end__":"save_memory"})

    builder.add_edge("tools","agent")

    builder.add_edge("save_memory",END)

    graph = builder.compile(
        checkpointer = checkpointer
    )

    return graph



