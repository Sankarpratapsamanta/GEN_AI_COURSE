import asyncio

import sys
from app.graph.checkpointer import (init_checkpointer,close_checkpointer)

from app.evaluation.rag.rag_runner import run_batch_rag_evaluation
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.graph.company_graph import create_company_graph

QUESTIONS_PATH="app/evaluation/rag/rag_questions.json"

async def main():
    try:
        checkpointer = await init_checkpointer()

        graph = await create_company_graph(checkpointer)

        results,summary = await run_batch_rag_evaluation(graph=graph,questions_path=QUESTIONS_PATH,user_role="employee")

        print(results)

        print("==================")

        print(summary)

    finally:
        await close_checkpointer()


if __name__ == "__main__":
    asyncio.run(main())