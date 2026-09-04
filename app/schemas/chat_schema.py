from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id:str
    user_role:str
    conversation_id: str
    message: str
