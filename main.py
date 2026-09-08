from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.schemas.chat_schema import ChatRequest
from app.agents.agent import create_company_agent
# from app.memory.store import (get_messages,add_message)
from app.database.session import AsyncSessionLocal
from app.memory.service import (get_messages,save_message,get_memory,save_memory)
from app.memory.extractor import extract_memory
from app.llm import llm
from app.graph.company_graph import create_company_graph
from app.graph.checkpointer import (init_checkpointer,close_checkpointer)
from langchain_core.messages import (HumanMessage)


graph = None

@asynccontextmanager
async def lifespan(app:FastAPI):
    global graph

    print("Starting AI Company Assistant")
    checkpointer = (await init_checkpointer())

    print("LangGraph checkpointer init")

    graph = await create_company_graph(checkpointer)

    print("LangGraph Agent init")

    yield

    print("Close LangGraph")
    await close_checkpointer()



app = FastAPI(
    title="AI Company Assistant",
    lifespan=lifespan
)

@app.post("/chat")
async def chat(request:ChatRequest):
    if graph is None:
        raise RuntimeError("Graph is not initialized")

    config = {
        "configurable":{
            "thread_id":request.conversation_id,
        },
        "recursion_limit":30
    }

    result = await graph.ainvoke(
        {
            "messages":[
                HumanMessage(content = request.message)
            ],
            "user_id":request.user_id,
            "user_role":request.user_role,
            "long_term_memory":[],
            "security_error":None,
            "blocked_tool_call_id":None,
        },
        config=config
    )

    final_message = result["structured_response"]

    return {
         "user_id":request.user_id,
         "conversation_id":request.conversation_id,
         "response":final_message.answer
     }



