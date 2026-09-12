from typing import Any

TOOL_POLICIES={
    "create_leave_request":{
        "allowed_roles":[
            "admin",
            "employee",
            "hr"
        ]
    },
    "create_new_employee":{
        "allowed_roles":[
            "admin",
            "hr"
        ]
    },
}


def validate_tool_arguments(tool_name:str, tool_arguments:Any):

    if tool_name == "create_leave_request":
        days = tool_arguments.get("days")

        if days is None:
            return False,"Leave days are required"

        if days <= 0:
            return False,"Leave days must be greater than 0"

        if days > 3:
            return False,"Leave request cannot exceed 3 days"

    if tool_name == "create_new_employee":

        employee_name = tool_arguments.get("employee_name")

        department = tool_arguments.get("department")

        if not employee_name:
            return False,"Employee name is required"

        if not department:
            return False,"Department name is required"


    return True,None

def authorize_tool(tool_name:str,user_role:str):
    policy = TOOL_POLICIES.get(tool_name)

    print("USER ROLE:", user_role)

    if policy is None:
        return True,None

    allowed_roles = policy["allowed_roles"]

    if user_role not in allowed_roles:
        return False,"You are not allowed to use this tool"

    return True,None

def check_tool_security(tool_name:str, tool_arguments:Any,user_role:str):
    valid,error = validate_tool_arguments(tool_name,tool_arguments)

    if not valid:
        return False , error

    authorized , error =authorize_tool(tool_name, user_role)

    if not authorized:
        return False,error

    return True,None

