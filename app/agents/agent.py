from langchain_groq import ChatGroq
from app.tools.company_tools import (get_employee_count,get_company_location,get_working_hours)
from langchain.agents import create_agent
from app.core.config import settings
from app.rag.retriever import search_company_documents



llm = ChatGroq(
    model = settings.groq_model,
    temperature=0,
    api_key=settings.groq_api_key
)

async def create_company_agent():
    functional_tools = [
        get_employee_count,
        get_company_location,
        get_working_hours
    ]

    rag_tools =[
        search_company_documents
    ]

    tools=(
        functional_tools
        + rag_tools
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