from app.tools.company_tools import (get_employee_count,get_company_location,get_working_hours)
from langchain.agents import create_agent
# from app.rag.retriever import search_company_documents
# from app.mcp_client.client import get_mcp_tools
from app.llm import llm




async def create_company_agent():
    functional_tools = [
        get_employee_count,
        get_company_location,
        get_working_hours
    ]

    # rag_tools =[
    #     search_company_documents
    # ]

    # mcp_tools=(await get_mcp_tools())

    tools=(
        functional_tools
        # + rag_tools
        # + mcp_tools
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
        You are an AI Company Assistant.
        Answer clearly and accurately.
        """
    )

    return agent