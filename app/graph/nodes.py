from langchain_core.messages import SystemMessage,AIMessage,ToolMessage
from app.llm import (llm,structured_llm)
from app.memory.service import (extract_memory,get_memory,save_memory)
from app.guardrails.tool_guardrail import check_tool_security

from app.graph.state import CompanyAgentState


async def load_memory(state:CompanyAgentState):
    memories = await get_memory(state["user_id"])
    return {
        "long_term_memory":memories,
    }

def create_agent_node(tools):
    llm_with_tools = llm.bind_tools(tools)

    async def agent(state:CompanyAgentState):
        memories = state.get("long_term_memory",[])

        if memories:
            memory_text = "\n".join(f"- {memory}" for memory in memories)
        else:
            memory_text = ("No long-term memory is available")

        system_message = SystemMessage(
            content=(
                f"""
                You are an AI Company Assistant.
                IMPORTANT:
                You must use an available tool whenever the user question can be answered using on of the available tools.
                
                Tool usage Rules:
                1. You must use an available tool whenever the user request requires company specific information.
                2. Never invent or guess company specific information.
                3. If an available tool can answer the user question call that tool.
                4. Do not provide the final answer before receiving the tool result.
                5. Carefully choose the tool that best matched the user request.
                6. Use the exact arguments required by the tool.
                7. Do not fabricate tool results.
                8. If no tool can answer the request, explain that the information is unavailable.
                
                PRIORITY
                
                Tool Calling > Direct Answer
                
                If a suitable tool exists, call it first. Do not answer from your own knowledge.
                Long-term memories about this user {memory_text}
                """
            ),
        )

        response = await  llm_with_tools.ainvoke([
            system_message,
            *state["messages"],
        ])


        print("LLM TOOL CALL:----", response.tool_calls)

        return {
            "messages":[
                response
            ]
        }
    return agent


async def save_company_memory(state:CompanyAgentState):
    if not state["messages"]:
        return {}

    human_messages=[
        message
        for message in state["messages"]
        if message.type == "human"
    ]

    if not human_messages:
        return {}

    latest_message = human_messages[-1]

    decision = await extract_memory(latest_message.content)

    if not decision.should_remember:
        return {}

    if decision.memory:
        await save_memory(user_id=state["user_id"],content=decision.memory)

    return {}


async def input_blocked_node(state:CompanyAgentState):
    return {
        "messages":[
            AIMessage(
                content=(
                    "I'm sorry , but I can't process this request."
                )
            )
        ]
    }

async def security_node(state:CompanyAgentState):
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    user_role = state["user_role"]
    security_messages=[]

    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args", {})

        is_safe, error = check_tool_security(tool_name=tool_name, tool_arguments=tool_args, user_role=user_role)

        if not is_safe:
            tool_call_id  = tool_call.get("id")

            if not isinstance(tool_call_id,str):
                continue
            security_messages.append(ToolMessage(
                content=str(error),
                tool_call_id=tool_call_id
            ))


    return {
        "messages":security_messages
    }

async def output_blocked_node(state:CompanyAgentState):
    return {
        "messages":[
            AIMessage(
                content=("I'm sorry , but I can't provides that information.")
            )
        ]
    }

async def structured_output_node(state:CompanyAgentState):
    res = await structured_llm.ainvoke([
        SystemMessage(
            content="""
            You are the final response formatter for an AI Company Assistant.
            
            Read the conversation and provide the final answer to the user.
            
            Return only the required structured response
            """
        ),*state["messages"],
    ])

    return {
        "structured_response":res
    }