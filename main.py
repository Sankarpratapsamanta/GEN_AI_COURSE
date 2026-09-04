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
            "blocked_tool_call_id":None
        },
        config=config
    )

    final_message = result["messages"][-1]

    return {
         "user_id":request.user_id,
         "conversation_id":request.conversation_id,
         "response":final_message.content
     }




# @app.post("/chat")
# async def chat(request:ChatRequest):
#
#     async with AsyncSessionLocal() as session:
#
#         # SHORT TERM MEMORY
#         history = await get_messages(session=session,user_id=request.user_id,conversation_id=request.conversation_id)
#
#         # LONG TERM MEMORY
#         memories = await get_memory(session=session,user_id=request.user_id)
#         print(history)
#
#         memory_context=""
#
#         if memories:
#             memory_context=(
#                 "Known information about the user:\n\n"
#                 +"\n".join(f"- {memory}" for memory in memories)
#             )
#
#         messages=[]
#
#         if memory_context:
#             messages.append({"role":"system","content":memory_context})
#
#         messages.extend(history)
#
#         messages.append({"role":"user","content":request.message})
#
#
#
#         await save_message(session=session,user_id=request.user_id,conversation_id=request.conversation_id,role="user",content=request.message)
#
#         agent = await create_company_agent()
#
#
#
#         print(messages)
#         res = await agent.ainvoke({
#             "messages":messages
#         })
#
#         final_answer = res["messages"][-1].content
#
#         await save_message(session=session, user_id=request.user_id, conversation_id=request.conversation_id,
#                            role="assistant", content=final_answer)
#
#         memory = await extract_memory(llm=llm,user_message=request.message,assistant_message=final_answer)
#
#         if memory:
#             await save_memory(session=session,user_id=request.user_id,content=memory)
#
#         return {
#             "user_id":request.user_id,
#             "conversation_id":request.conversation_id,
#             "response":final_answer
#         }



