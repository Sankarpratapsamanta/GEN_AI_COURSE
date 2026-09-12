from langchain_groq import ChatGroq
from app.core.config import settings
from app.schemas.assistant_schema import CompanyAssistantResponse

llm = ChatGroq(
    model = settings.groq_model,
    temperature=0,
    api_key=settings.groq_api_key
)

structured_llm=llm.with_structured_output(CompanyAssistantResponse)
