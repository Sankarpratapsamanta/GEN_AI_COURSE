from pydantic import BaseModel,Field

class RAGEvaluation(BaseModel):
    context_relevance_score:int=Field(description="How relevant the retrieved context is to the question.")
    context_precision_score:int=Field(description="How much of the retrieved context is useful for answering the question.")
    context_recall_score:int=Field(description="Whether the retrieved context contains the information needed to answer the question.")
    faithfulness_score:int=Field(description="Whether the answer is supported by te retrieved context.")
    answer_relevance_score:int=Field(description="Whether the answer directly addresses the question.")
    explanation:str=Field(description="Brief explanation of the evaluation.")
    

class RAGEvaluationResult(BaseModel):
    question_id:str
    question:str
    answer:str
    contexts:list[str]
    context_relevance_score:int
    context_precision_score:int
    context_recall_score:int
    faithfulness_score:int
    answer_relevance_score:int

    average_score:float
    latency_seconds:float
    passed:bool
    explanation:str
    error:str|None=None

class RAGEvaluationSummary(BaseModel):
    total_questions:int
    successful_questions:int
    failed_questions:int

    average_context_relevance_score:float
    average_context_precision_score:float
    average_context_recall_score:float
    average_faithfulness_score:float
    average_answer_relevance_score:float

    overall_average_score:float

    average_latency_seconds:float

    pass_rate:float