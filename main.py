from fastapi import FastAPI
from app.core.config import settings
from app.schemas.chat_schema import ChatRequest
from langchain_groq import ChatGroq

app = FastAPI(
    title="AI Company Assistant",
)

llm = ChatGroq(
    model = settings.groq_model,
    temperature=0,
    api_key=settings.groq_api_key
)

@app.post("/chat")
async def chat(request:ChatRequest):
    res = await llm.ainvoke(
        request.message
    )

    return {
        "response":res.content
    }



