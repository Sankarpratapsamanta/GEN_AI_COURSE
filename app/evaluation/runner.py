import time
import uuid
from langchain_core.messages import  AIMessage,HumanMessage
from app.schemas.assistant_schema import CompanyAssistantResponse

def extract_tool_call(messages):
    tool_calls=[]

    for message in messages:
        if not isinstance(message,AIMessage):
            continue
        for tool_call in getattr(message,"tool_calls",[]):
            tool_calls.append({
                "name":tool_call.get("name"),
                "args":tool_call.get("args",{}),
            })
    return tool_calls


def evaluate_tool_selection(expected_tools,actual_tool_calls):
    actual_tool=[
        tool["name"]
        for tool in actual_tool_calls
    ]

    print("ACTUAL AND EXPECTED TOOLS : ", actual_tool, expected_tools )

    return expected_tools == actual_tool

def evaluate_tool_arguments(expected_args,actual_tool_calls):
    if len(expected_args)!=len(actual_tool_calls):
        return False
    for expected_arg,actual_arg in zip(expected_args,actual_tool_calls):

        if expected_arg != actual_arg.get("args",{}):
            return False
    return True

def evaluate_structured_output(result):
    structured_output=result.get("structured_response",{})

    return isinstance(structured_output,CompanyAssistantResponse)

def evaluate_behaviour(expected_behaviour,result):
    structured_output = result.get("structured_response", {})

    if expected_behaviour == "answer":
        return structured_output is not None

    if expected_behaviour == "blocked":
        return structured_output is None

    return False



async def run_evaluation_case(graph,test_case):
    start_time = time.perf_counter()

    try:
        result = await graph.ainvoke(
            {
                "messages":[
                    HumanMessage(
                        content=test_case["question"]
                    )
                ],
                "user_id":"eval-user-1",
                "user_role":test_case["user_role"],
                "long_term_memory":[],
                "security_error":None,
                "blocked_tool_call_id":None
            },
            config={
                "configurable":{
                    "thread_id":{
                        f"evaluation-{test_case['id']}-{uuid.uuid4()}"
                    }
                }
            }
        )

        latency = time.perf_counter() - start_time

        messages = result.get("messages",[])

        for message in messages:
            print("Tool Calls:" , getattr(message,"tool_calls",[]))

        actual_tool_calls=(extract_tool_call(messages))

        print("ACTUAL TOOL CALL:-----",actual_tool_calls)

        expected_tools = test_case.get("expected_tools",[])

        expected_args=test_case.get("expected_tool_args",[])

        expected_behaviour=test_case.get("expected_behaviour")

        tool_selection_passed=(evaluate_tool_selection(expected_tools,actual_tool_calls))

        tool_argument_passed=(evaluate_tool_arguments(expected_args,actual_tool_calls))

        structured_output_passed = evaluate_structured_output(result)

        behaviour_passed=(evaluate_behaviour(expected_behaviour,result))


        if expected_behaviour == "answer":
            passed = (
                tool_argument_passed and tool_argument_passed and structured_output_passed and behaviour_passed
            )
        else:
            passed = (
                tool_selection_passed and tool_argument_passed and behaviour_passed
            )


        final_response = result.get("structured_response")

        answer = None

        if final_response:
            answer = final_response.answer

        return {
            "test_id":test_case["id"],
            "question":test_case["question"],
            "expected_tools":expected_tools,
            "actual_tool_calls":[tool["name"] for tool in actual_tool_calls],
            "expected_tool_args":expected_args,
            "actual_tool_args":[tool["args"] for tool in actual_tool_calls],
            "tool_selection_passed":tool_selection_passed,
            "tool_argument_passed":tool_argument_passed,
            "structured_output_passed":structured_output_passed,
            "behaviour_passed":behaviour_passed,
            "expected_behaviour":expected_behaviour,
            "passed":passed,
            "answer":answer,
            "latency":round(latency,3),
            "error":None
        }
    except Exception as e:
        latency = time.perf_counter() - start_time
        return {
            "test_id": test_case["id"],
            "question": test_case["question"],
            "expected_tools": test_case["expected_tools"],
            "actual_tool_calls": [],
            "expected_tool_args": test_case["expected_tools"],
            "actual_tool_args": [],
            "tool_selection_passed": False,
            "tool_argument_passed": False,
            "structured_output_passed": False,
            "behaviour_passed": False,
            "expected_behaviour": test_case["expected_behaviour"],
            "passed": False,
            "answer": None,
            "latency": round(latency, 3),
            "error": str(e)
        }




async  def run_evaluation(graph,dataset):
    results = []

    for test_case in dataset:

        result = await run_evaluation_case(graph,test_case)
        results.append(result)


        print(f"Test ID: {test_case['id']}")
        print(f"Question: {test_case['question']}")
        print(f"Tool Selection: {result['tool_selection_passed']}")

        print(f"Tool Arguments: {result['tool_argument_passed']}")
        print(f"Structured Output: {result['structured_output_passed']}")
        print(f"Behavior: {result['behaviour_passed']}")
        print(f"Overall: {'PASS' if result['passed'] else 'FAIL'}")
        print(f"Latency: {result['latency']} sec")



    return results


def calculate_summary(results):

    total = len(results)
    if total == 0:
        return {
            "total":0,
            "passed":0,
            "failed":0,
            "pass_rate":0
        }
    passed = sum(1 for result in results if result["passed"])

    failed = total - passed
    pass_rate = (passed / total) * 100

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(pass_rate,2)
    }


