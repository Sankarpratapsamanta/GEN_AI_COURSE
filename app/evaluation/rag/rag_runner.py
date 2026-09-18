import time
from pathlib import Path
import json
import uuid
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from app.evaluation.rag.rag_schema import (RAGEvaluationResult,RAGEvaluationSummary)
from app.evaluation.rag.rag_judge import evaluate_rag

RAG_TOOL_NAME = "search_company_documents"
PASS_THRESHOLD=4.0

async def extract_rag_context(messages):
    contexts=[]

    for message in messages:
        if not isinstance(message,ToolMessage):
            continue
        if message.name != RAG_TOOL_NAME:
            continue
        if isinstance(message.content,str):
            contexts.append(message.content)
        else:
            contexts.append(str(message.content))

    return contexts


async def extract_final_answer(messages):
    for message in reversed(messages):
        if not isinstance(message,AIMessage):
            continue
        if message.tool_calls:
            continue

        if isinstance(message.content,str):
            return message.content
        return str(message.content)
    return ""

async def evaluate_single_question(graph,question_id,question,user_role):
    start_time = time.perf_counter()

    try:
        thread_id=(
            f"rag-eval-{question_id}-{uuid.uuid4()}"
        )

        result = await graph.ainvoke({
            "messages":[
                HumanMessage(content=question)
            ],
            "user_id":"rag-eval-1",
            "user_role":user_role,
            "long_term_memory":[],
            "security_error":None,
            "blocked_tool_call_id":None
        },config={
            "configurable":{
                "thread_id":thread_id
            },
            "recursion_limit":30
        })

        latency = time.perf_counter() - start_time

        messages = result.get("messages",[])

        contexts = await extract_rag_context(messages)

        answer = await extract_final_answer(messages)

        if not answer:
            return RAGEvaluationResult(
                question_id=question_id,
                question=question,
                answer="",
                contexts=contexts,
                context_relevance_score=0,
                context_precision_score=0,
                context_recall_score=0,
                faithfulness_score=0,
                answer_relevance_score=0,

                average_score=0,
                latency_seconds=round(latency,3),
                passed=False,
                explanation="No final answer",
                error="No final answer"
            )
        evaluation = await evaluate_rag(question=question,contexts=contexts,answer=answer)

        scores=[
            evaluation.context_relevance_score,
            evaluation.context_precision_score,
            evaluation.context_recall_score,
            evaluation.faithfulness_score,
            evaluation.answer_relevance_score
        ]


        average_score = sum(scores) / len(scores)

        passed = average_score >= PASS_THRESHOLD

        return RAGEvaluationResult(
            question_id=question_id,
            question=question,
            answer=answer,
            contexts=contexts,
            context_relevance_score=evaluation.context_relevance_score,
            context_precision_score=evaluation.context_precision_score,
            context_recall_score=evaluation.context_recall_score,
            faithfulness_score=evaluation.faithfulness_score,
            answer_relevance_score=evaluation.answer_relevance_score,

            average_score=round(average_score,2),
            latency_seconds=round(latency, 3),
            passed=passed,
            explanation=evaluation.explanation,
            error=None
        )
    except Exception as e:
        latency = time.perf_counter() - start_time
        return RAGEvaluationResult(
            question_id=question_id,
            question=question,
            answer="",
            contexts=[],
            context_relevance_score=0,
            context_precision_score=0,
            context_recall_score=0,
            faithfulness_score=0,
            answer_relevance_score=0,

            average_score=0,
            latency_seconds=round(latency, 3),
            passed=False,
            explanation="Evaluation Failed",
            error=str(e)
        )


async def build_summary(results:list[RAGEvaluationResult]):
    total = len(results)

    successful=[
        result
        for result in results
        if result.error is None
    ]

    failed = [
        result
        for result in results
        if result.error is not None
    ]

    if not successful:
        return RAGEvaluationSummary(
            total_questions=total,
            successful_questions=0,
            failed_questions=len(failed),

            average_context_relevance_score=0,
            average_context_precision_score=0,
            average_context_recall_score=0,
            average_faithfulness_score=0,
            average_answer_relevance_score=0,

            overall_average_score=0,

            average_latency_seconds=0,

            pass_rate=0
        )


    print("AVGSGSGSG",)

    average_context_relevance = round(sum(result.context_relevance_score for result in successful) / len(successful),2)

    average_precision_score = round(sum(result.context_precision_score for result in successful) / len(successful),2)

    average_recall_score = round(sum(result.context_recall_score for result in successful) / len(successful),2)
    average_faithfulness_score = round(sum(result.faithfulness_score for result in successful) / len(successful),2)
    average_answer_relevance_score = round(sum(result.answer_relevance_score for result in successful) / len(successful),2)
    overall_average_score = round(sum(result.average_score for result in successful) / len(successful),2)

    average_latency = round(sum(result.latency_seconds for result in successful) / len(successful),2)

    passed = [result for result in successful if result.passed]

    pass_rate = round(len(passed)/len(successful),2)

    return RAGEvaluationSummary(
        total_questions=total,
        successful_questions=len(successful),
        failed_questions=len(failed),

        average_context_relevance_score=average_context_relevance,
        average_context_precision_score=average_precision_score,
        average_context_recall_score=average_recall_score,
        average_faithfulness_score=average_faithfulness_score,
        average_answer_relevance_score=average_answer_relevance_score,

        overall_average_score=overall_average_score,

        average_latency_seconds=average_latency,

        pass_rate=pass_rate
    )


async def run_batch_rag_evaluation(graph,questions_path:str,user_role:str="employee"):

    path = Path(questions_path)

    with path.open("r",encoding="utf-8") as f:
        questions = json.load(f)
    results=[]

    for index,item in enumerate(questions,start=1):

        question_id = item["id"]
        question = item["question"]

        result = await evaluate_single_question(graph=graph,question_id=question_id,question=question,user_role=user_role)

        results.append(result)

    summary = await build_summary(results)

    return results,summary