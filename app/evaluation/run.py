import asyncio
import sys
from app.graph.checkpointer import (init_checkpointer,close_checkpointer)

from app.graph.company_graph import create_company_graph

from app.evaluation.dataset import evaluation_dataset
from app.evaluation.runner import run_evaluation,calculate_summary


if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

async def main():
    try:
        checkpointer = await init_checkpointer()

        graph = await create_company_graph(checkpointer)

        results = await run_evaluation(graph,evaluation_dataset)

        summary = calculate_summary(results)

        print("EVALUATION RESULTS")

        print(f"Total test: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass rate: {summary['pass_rate']}")


    finally:
        await close_checkpointer()


if __name__ == "__main__":
    asyncio.run(main())