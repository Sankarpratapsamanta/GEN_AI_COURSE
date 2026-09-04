from langgraph.graph import (StateGraph,START,END)

from langgraph.prebuilt import (ToolNode,tools_condition)
from app.graph.state import CompanyAgentState
from app.graph.nodes import (load_memory,create_agent_node,save_company_memory,input_blocked_node,security_node,output_blocked_node)
from app.graph.routers import (input_guardrail_router,tool_guardrail_router,output_guardrail_router)
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

    builder.add_node("input_guardrail",lambda state:state)
    builder.add_node("input_blocked",input_blocked_node)
    builder.add_node("output_blocked",output_blocked_node)
    builder.add_node("output_guardrail", lambda state: state)

    builder.add_node("security",security_node)

    builder.add_edge(
        START,
        "input_guardrail",
    )

    builder.add_conditional_edges(
        "input_guardrail",
        input_guardrail_router,
        {
            "agent":"load_memory",
            "blocked":"input_blocked"
        }
    )

    builder.add_edge(
        "input_blocked",
        END
    )

    builder.add_edge(
        "load_memory",
        "agent",
    )

    builder.add_conditional_edges("agent",
                                  tool_guardrail_router,
                                  {
                                      "tools":"tools",
                                      "security":"security",
                                      "agent":"output_guardrail"
                                  })

    # builder.add_conditional_edges("agent",tools_condition,{"tools":"tools","__end__":"save_memory"})

    builder.add_edge("tools","agent")

    builder.add_edge("security","agent")

    builder.add_conditional_edges("output_guardrail",output_guardrail_router,{"safe":"save_memory","blocked":"output_blocked"})

    builder.add_edge("output_blocked",END)

    builder.add_edge("save_memory",END)

    graph = builder.compile(
        checkpointer = checkpointer
    )

    return graph



