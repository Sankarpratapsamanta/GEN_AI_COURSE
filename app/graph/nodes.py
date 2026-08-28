from langchain_core.messages import SystemMessage
from app.llm import llm
from app.memory.service import (extract_memory,get_memory,save_memory)

from app.graph.state import CompanyAgentState


async def load_memory(state:CompanyAgentState):
    memories = await get_memory(state["user_id"])

    print("User ID", state["user_id"])
    print("Memories", memories)
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
                Use available tools when necessary.
                Long-term memories about this user {memory_text}
                """
            ),
        )

        response = await  llm_with_tools.ainvoke([
            system_message,
            *state["messages"],
        ])


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
