from fastapi import FastAPI
from app.core.config import settings
from app.schemas.chat_schema import ChatRequest
from langchain_groq import ChatGroq
from app.tools.company_tools import (get_employee_count,get_company_location,get_working_hours)
from langchain.agents import create_agent

app = FastAPI(
    title="AI Company Assistant",
)

llm = ChatGroq(
    model = settings.groq_model,
    temperature=0,
    api_key=settings.groq_api_key
)


tools=[
    get_employee_count,
    get_company_location,
    get_working_hours
]


agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    You are an AI Company Assistant.
    Answer clearly and accurately.
    """
)


@app.post("/chat")
async def chat(request:ChatRequest):

    res = await agent.ainvoke({
        "messages":[
            {
                "role":"user",
                "content":request.message
            }
        ]
    })

    return {
        "response":res["messages"][-1].content
    }



