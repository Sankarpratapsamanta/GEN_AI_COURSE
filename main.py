from fastapi import FastAPI
from app.schemas.chat_schema import ChatRequest
from app.agents.agent import create_company_agent

app = FastAPI(
    title="AI Company Assistant",
)

@app.post("/chat")
async def chat(request:ChatRequest):

    agent = await create_company_agent()
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



