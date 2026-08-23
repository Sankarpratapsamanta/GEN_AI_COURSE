from fastapi import FastAPI
from app.schemas.chat_schema import ChatRequest
from app.agents.agent import create_company_agent
# from app.memory.store import (get_messages,add_message)
from app.database.session import AsyncSessionLocal
from app.memory.service import (get_messages,save_message,get_memory,save_memory)
from app.memory.extractor import extract_memory
from app.llm import llm

app = FastAPI(
    title="AI Company Assistant",
)

@app.post("/chat")
async def chat(request:ChatRequest):

    async with AsyncSessionLocal() as session:

        # SHORT TERM MEMORY
        history = await get_messages(session=session,user_id=request.user_id,conversation_id=request.conversation_id)

        # LONG TERM MEMORY
        memories = await get_memory(session=session,user_id=request.user_id)
        print(history)

        memory_context=""

        if memories:
            memory_context=(
                "Known information about the user:\n\n"
                +"\n".join(f"- {memory}" for memory in memories)
            )

        messages=[]

        if memory_context:
            messages.append({"role":"system","content":memory_context})

        messages.extend(history)

        messages.append({"role":"user","content":request.message})



        await save_message(session=session,user_id=request.user_id,conversation_id=request.conversation_id,role="user",content=request.message)

        agent = await create_company_agent()



        print(messages)
        res = await agent.ainvoke({
            "messages":messages
        })

        final_answer = res["messages"][-1].content

        await save_message(session=session, user_id=request.user_id, conversation_id=request.conversation_id,
                           role="assistant", content=final_answer)

        memory = await extract_memory(llm=llm,user_message=request.message,assistant_message=final_answer)

        if memory:
            await save_memory(session=session,user_id=request.user_id,content=memory)

        return {
            "user_id":request.user_id,
            "conversation_id":request.conversation_id,
            "response":final_answer
        }



