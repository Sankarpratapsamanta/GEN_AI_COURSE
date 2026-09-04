from langchain_groq import ChatGroq
from app.core.config import settings

llm = ChatGroq(
    model = settings.groq_model,
    temperature=0,
    api_key=settings.groq_api_key
)