from fastapi import FastAPI
from langchain_core import documents

from app.core.config import settings
from app.schemas.chat_schema import ChatRequest
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
# from app.rag.retriever import retriever
from app.tools.company_tools import (get_employee_count,get_company_location,get_working_hours)
from langchain_core.messages import ToolMessage

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

llm_with_tools = llm.bind_tools(tools)

tool_map={
    "get_employee_count":get_employee_count,
    "get_company_location":get_company_location,
    "get_working_hours":get_working_hours
}

prompt = ChatPromptTemplate.from_messages([
    {
        "role":"system",
        "content":"""
        You are an AI Company Assistant.
        Answer clearly and accurately.
        """
    },
    {
        "role":"human",
        "content":"""
        Question:
        {question}
        """
    }
])

chain = prompt | llm_with_tools

@app.post("/chat")
async def chat(request:ChatRequest):

    # documents = await retriever.ainvoke(
    #     request.message
    # )
    # context = "\n\n".join(
    #     document.page_content
    #     for document in documents
    # )

    res = await chain.ainvoke({
        "question": request.message
    })

    if not res.tool_calls:
        return {
            "response": res.content
        }

    tool_messages=[]

    for tool_call in res.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool = tool_map[tool_name]
        tool_result = await tool.ainvoke(tool_args)

        tool_message = ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"]
        )

        tool_messages.append(tool_message)


    print(tool_messages)
    final_answer = await llm.ainvoke([res,*tool_messages])

    return {
        "response":final_answer.content
    }



