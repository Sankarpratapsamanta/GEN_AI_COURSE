from langchain_core.tools import (StructuredTool)
from app.graph.retry import execute_with_retry

def make_retryable_tool(tool):

    async def retryable_coroutine(**kwargs):
        async def execute():
            return await tool.ainvoke(kwargs)
        return await execute_with_retry(execute)

    retryable_tool = StructuredTool.from_function(
        coroutine=retryable_coroutine,
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        response_format=getattr(tool, "response_format", "content"),
    )

    return retryable_tool


def make_all_tools_retryable(tools):
    retryable_tools = []

    for tool in tools:
        retryable_tool = make_retryable_tool(tool)
        retryable_tools.append(retryable_tool)

    return retryable_tools