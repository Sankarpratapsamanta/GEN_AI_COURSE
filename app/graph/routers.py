from app.guardrails.input_guardrail import check_input_security
from app.guardrails.tool_guardrail import check_tool_security
from app.guardrails.output_guardrail import check_output_security

def input_guardrail_router(state):
    if not state["messages"]:
        return "blocked"

    message = state["messages"][-1]

    content = message.content

    is_safe , error = check_input_security(content)

    if not is_safe:
        return "blocked"

    return "agent"

def tool_guardrail_router(state):
    last_message = state["messages"][-1]

    print("Tool Guardrail Call:", last_message)

    tool_calls = getattr(last_message,"tool_calls",[])
    print("Tool Call:", tool_calls)
    if not tool_calls:
        return "agent"

    user_role = state["user_role"]

    for tool_call in tool_calls:

        tool_name = tool_call["name"]
        tool_args = tool_call.get("args",{})

        print("TOOL NAME:",tool_name)
        print("TOOL ARGS:", tool_args)
        print("USER ROLE:",user_role)

        is_safe,error = check_tool_security(tool_name=tool_name,tool_arguments=tool_args,user_role=user_role)

        if not is_safe:
            return "security"

    return "tools"

def output_guardrail_router(state):
    if not state["messages"]:
        return "blocked"

    last_message = state["messages"][-1]

    content = last_message.content

    is_safe,error = check_output_security(content)

    if not is_safe:
        return "blocked"

    return "safe"