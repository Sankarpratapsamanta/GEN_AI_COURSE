from fastapi import FastAPI
from langchain_core import documents

from app.core.config import settings
from app.schemas.chat_schema import ChatRequest
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.rag.retriever import retriever

app = FastAPI(
    title="AI Company Assistant",
)

llm = ChatGroq(
    model = settings.groq_model,
    temperature=0,
    api_key=settings.groq_api_key
)

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
        Context:
        {context}
        
        Question:
        {question}
        """
    }
])

chain = prompt | llm

@app.post("/chat")
async def chat(request:ChatRequest):

    documents = await retriever.ainvoke(
        request.message
    )
    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    res = await chain.ainvoke({
        "context":context,
        "question": request.message
    })

    return {
        "response":res.content
    }



