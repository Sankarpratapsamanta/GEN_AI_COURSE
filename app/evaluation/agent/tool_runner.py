import time
from langchain_core.messages import AIMessage,HumanMessage
from app.evaluation.agent.tool_schema import ToolEvalSchema,ToolEvalResult
import uuid



def extract_tool_calls(messages):

    tool_calls = []
    for message in messages:
        if not isinstance(message,AIMessage):
            continue
        if not message.tool_calls:
            continue
        for tool_call in message.tool_calls:
            tool_calls.append(
                {
                    "name":tool_call.get("name"),
                    "args":tool_call.get("args",{}),
                    "id":tool_call.get("id"),
                }
            )
    return tool_calls


def extract_tool_names(tool_calls):
    return [
        tool_call["name"]
        for tool_call in tool_calls
    ]


def normalize_value(value):
    if isinstance(value,str):
        return value.strip()
    return value


def validate_tool_arguments(expected_arguments,actual_arguments):
    if not expected_arguments:
        return True

    for key,expected_value in expected_arguments.items():
        if key not in actual_arguments:
            return False
        actual_value = actual_arguments[key]

        if(normalize_value(actual_value) != normalize_value(expected_value)):
            return False
    return True


def validate_all_arguments(case,tool_calls):
    if not case.expected_arguments:
        return True
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        expected = (
            case.expected_arguments.get(tool_name)
        )

        if expected is None:
            continue
        actual = tool_call.get("args",{})

        if not validate_tool_arguments(expected,actual):
            return False

    return True



def extract_final_answer(messages):
    for message in reversed(messages):
        if not isinstance(message,AIMessage):
            continue
        if message.tool_calls:
            continue
        if isinstance(message.content,str):
            return message.content
        return str(message.content)
    return ""


async def evaluate_tool_case(graph,case,user_role):
    start_time = time.perf_counter()
    try:
        thread_id = (
            f"tool-eval-{case.id}-{uuid.uuid4()}"
        )

        result = await graph.ainvoke(
            {
                "messages":[
                    HumanMessage(content=case.question)
                ],
                "user_id":"tool-evaluation-user",
                "user_role":user_role,
                "long_term_memory":[],
                "security_error":None,
                "blocked_tool_call_id":None
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                },
                "recursion_limit": 30
            }
        )

        latency = time.perf_counter() - start_time

        messages = result.get("messages",[])


        tool_calls = extract_tool_calls(messages)

        actual_tools = extract_tool_names(tool_calls)

        tool_was_called = bool(actual_tools)


        if case.should_call_tool:
            tool_selection_correct = (
                len(actual_tools) > 0 and actual_tools[0] == case.expected_tools[0]
            )
        else:
            tool_selection_correct = (len(actual_tools) == 0)

        tool_sequence_correct = (
            actual_tools == case.expected_tools
        )

        unexpected_tool_call = False

        if actual_tools != case.expected_tools:
            unexpected_tool_call = True

        arguments_correct = (
            validate_all_arguments(case,tool_calls)
        )

        final_answer = extract_final_answer(messages)

        passed = (tool_selection_correct and tool_sequence_correct and arguments_correct and not unexpected_tool_call)


        return ToolEvalResult(
            case_id=case.id,
            question=case.question,
            expected_tools=case.expected_tools,
            actual_tools=actual_tools,
            should_call_tool=case.should_call_tool,
            tool_was_called=tool_was_called,
            tool_selection_correct=tool_selection_correct,
            tool_sequence_correct=tool_sequence_correct,
            unexpected_tool_call=unexpected_tool_call,
            arguments_correct=arguments_correct,
            final_answer=final_answer,
            passed=passed,
            latency_seconds = round(latency, 2),
            error = None
        )

    except Exception as e:
        latency = time.perf_counter() - start_time

        return ToolEvalResult(
            case_id=case.id,
            question=case.question,
            expected_tools=case.expected_tools,
            actual_tools=[],
            should_call_tool=case.should_call_tool,
            tool_was_called=False,
            tool_selection_correct=False,
            tool_sequence_correct=False,
            unexpected_tool_call=False,
            arguments_correct=False,
            final_answer="",
            passed=False,
            latency_seconds=round(latency, 2),
            error=str(e)
        )



async def run_batch_tool_eval(graph,cases:list[ToolEvalSchema],user_role:str="employee"):
    results=[]

    for index,case in enumerate(cases,start=1):
        result = await evaluate_tool_case(graph=graph,case=case,user_role=user_role)

        results.append(result)

    return results