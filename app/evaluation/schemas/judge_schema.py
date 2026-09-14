from pydantic import BaseModel,Field

class LLMJudgeResponse(BaseModel):
    correctness_score:int=Field(
        description="Score from 1 to 5 for factual correctness",
    )
    relevance_score:int=Field(
        description="Score from 1 to 5 for how well the answer addresses the user question",
    )

    groundedness_score:int=Field(
        description="Score from 1 to 5 for how well the answer supported by the provided context",
    )

    completeness_score:int=Field(
        description="Score from 1 to 5 for whether the answer contains all important information needed to answer the question.",
    )

    clarity_score:int=Field(
        description="Score from 1 to 5 for how clear and understandable the answer is",
    )

    explanation:str=Field(
        description="Brief explanation of the evaluation.",
    )
