from fastapi import FastAPI
from app.core.config import settings
from app.schemas.chat_schema import ChatRequest
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI(
    title="AI Company Assistant",
)

llm = ChatGroq(
    model = settings.groq_model,
    temperature=0,
    api_key=settings.groq_api_key
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an AI Company Assistant.
        Answer clearly and accurately.
        """
    ),
    (
        "human",
        "{question}"
    )
])

@app.post("/chat")
async def chat(request:ChatRequest):

    messages = prompt.invoke({
        "question":request.message
    })
    res = await llm.ainvoke(
        messages
    )

    return {
        "response":res.content
    }



