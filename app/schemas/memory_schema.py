from pydantic import BaseModel,Field

class MemoryDecision(BaseModel):
    should_remember:bool = Field(
        description=(
            "Whether the user message contains useful information that should be remembered across conversations."
        )
    )

    memory:str|None = Field(
        default=None,
        description=(
            "The concise fact that should be remembered."
        )
    )