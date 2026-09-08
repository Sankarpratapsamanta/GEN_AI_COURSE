from pydantic import BaseModel,Field

class CompanyAssistantResponse(BaseModel):
    answer:str=Field(
        description="The final answer to the user request"
    )