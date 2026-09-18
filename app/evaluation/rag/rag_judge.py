from langchain_core.messages import HumanMessage,SystemMessage
from app.llm import llm

from app.evaluation.rag.rag_schema import RAGEvaluation

rag_evaluation_llm = llm.with_structured_output(RAGEvaluation)

async def evaluate_rag(question:str,contexts:list[str],answer:str):

    prompt=f"""
    You are an evaluator for a RAG system.
    Evaluate the Rag response using the following information:
    
    User Question:
    {question}
    
    Retrieved Context:
    {contexts}
    
    Assistant Answer:
    {answer}
    
    
    Evaluate these five criteria:
    
    1- Context Relevance
    
    Does the retrieved context relate to the user question?
    
    5 = Highly Relevant
    4 = Mostly Relevant
    3 = Moderately Relevant
    2 = Slightly Relevant
    1 = Not Relevant
    
    2- Context Precision
    
    How much of the retrieved context is useful for answering the user question?
    
    5 = Almost everything is useful
    4 = Most is useful
    3 = Some is useful
    2 = Little is useful
    1 = Almost everything is irrelevant.
    
    3- Context Recall
    
    Does the retrieved context contain the information required to answer the user question?
    
    5 = All required information is present
    4 = Almost all required information is present
    3 = Most required information is present
    2 = Important information is missing
    1 = Most required information is missing
    
    4- Faithfulness
    
    Is the assistant answer supported by the retrieved context?
    
    5 = Completely Supported
    4 = Mostly Supported
    3 = Partly Supported
    2 = Mostly Unsupported
    1 = Unsupported
    
    5- Answer Relevance
    
    Does the answer directly address the user question?
    
    5 = Directly and completely answer the user question
    4 = Directly answers the question with minor issues
    3 = Partly answers the question
    2 = Mostly does not answer the question
    1 = Does not answer the question
    
    
    SCORING:
    1= Very Good
    2= Poor
    3= Acceptable
    4= Good
    5= Excellent
    
    Important:
    - Be strict and objective.
    - Use only the provided question.
    - Do not use outside knowledge.
    
    Return the evaluation using the required structured.
    """

    result = await rag_evaluation_llm.ainvoke(
        [
            SystemMessage(
                content="You are a strict and objective RAG evaluator"
            ),
            HumanMessage(content=prompt)
        ]
    )

    return result




