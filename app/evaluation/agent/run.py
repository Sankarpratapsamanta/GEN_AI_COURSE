import asyncio

import sys
from app.graph.checkpointer import (init_checkpointer,close_checkpointer)
from app.evaluation.agent.tool_schema import ToolEvalSchema
from app.evaluation.agent.tool_runner import run_batch_tool_eval

import json
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.graph.company_graph import create_company_graph

QUESTIONS_PATH="app/evaluation/agent/tool_questions.json"


def load_test_case():
    with open(QUESTIONS_PATH,"r",encoding="utf-8") as f:
        data = json.load(f)
    return [
        ToolEvalSchema(**item)
        for item in data
    ]

async def main():
    try:
        checkpointer = await init_checkpointer()

        graph = await create_company_graph(checkpointer)

        cases = load_test_case()

        result = await run_batch_tool_eval(graph=graph,cases=cases,user_role="employee")


        print("RESULT:",result)

    finally:
        await close_checkpointer()


if __name__ == "__main__":
    asyncio.run(main())