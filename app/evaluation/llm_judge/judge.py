from langchain_core.messages import SystemMessage,HumanMessage
from app.llm import llm
from app.evaluation.schemas.judge_schema import LLMJudgeResponse

judge_llm = llm.with_structured_output(LLMJudgeResponse)


async def evaluate_answer(question:str,answer:str,context:str):
    prompt=f"""
    You are an evaluator for an AI Company Assistant.
    
    Your task is to evaluate the assistant answer against the user question and the available context.
    
    CRITERIA
    
    Correctness:
    Is the answer factually correct based on the provided context.
    
    Relevance:
    Does the answer directly address the user question?
    
    Groundedness:
    Is the answer supported by the provided context?
    The assistant should not invent information that is not supported by the provided context.
    
    Completeness:
    Does the answer contain all the important information required to properly answer the user question?
    
    Clarity:
    Is the answer clear , understandable and easy to follow ?
    
    SCORING 
    
    Give each criteria a score from 1 to 5.
    
    1= Very Poor
    2= Poor
    3= Acceptable
    4= Good
    5= Excellent
    
    IMPORTANT
    
    Evaluate the answer based on the user question and the available context.
    
    Do not give a high score simply because the answer sound confident.
    
    If important information is missing , reduce the completeness score.
    
    User Question:
    {question}
    
    Assistant Answer:
    {answer}
    
    Available Context:
    {context}
    
    Return the evaluation in the required structured format.
    """

    result = await judge_llm.ainvoke([
        SystemMessage(
            content="You are a strict AI evaluator"
        ),
        HumanMessage(content=prompt)
    ])

    return result

