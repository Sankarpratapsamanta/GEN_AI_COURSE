import asyncio
from app.evaluation.llm_judge.judge import evaluate_answer
import sys


if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

async def main():
    result=await evaluate_answer(
        question="Where is the company located?",
        answer="The company is located in Mumbai",
        context="The company headquarters is located in Mumbai."
    )

    print("Correctness:" , result.correctness_score)
    print("Relevance:" , result.relevance_score)
    print("Groundedness:", result.groundedness_score)
    print("Completeness:",result.completeness_score)
    print("Clarity:", result.clarity_score)
    print("Explain About LLM EVAL:", result.explanation)


if __name__ == "__main__":
    asyncio.run(main())