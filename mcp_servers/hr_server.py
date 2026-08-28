from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HR MCP SERVER")

@mcp.tool(description="Get employee information.")
def get_employee_profile(employee_name:str):
    employees={
        "Alice":"Alice is a Senior Python Developer in the Engineering Department",
        "Bob":"Bob is a Backend Developer in the Engineering Department",
        "Emma":"Emma is an HR manager"
    }

    return employees.get(employee_name,
                 f"No employee found for"
                        f"{employee_name}"
                        )

@mcp.tool(description="Create an employee leave request.")
def create_leave_request(employee_name:str,days:int,reason:str):
    if days <= 0:
        return "Leave days must be greater than 0"

    return (
        f"Leave request created for {employee_name}. Days :{days}. Reason:{reason}"
    )

@mcp.tool(description="Create an new employee request.")
def create_new_employee(employee_name:str,department:str):
    return (
        f"{employee_name} with:{department} is successfully created."
    )

@mcp.resource("hr://working-hours")
def working_hours():
    return (
        "Company working hours are 9AM to 6PM"
    )

@mcp.prompt()
def employee_review(employee_name):
    return (
        f"""
        Create a professional performance
        review for {employee_name}
        
        Include:
        -Strengths
        -Areas for improvement
        """
    )

if __name__ == "__main__":
    mcp.settings.host="127.0.0.1"
    mcp.settings.port=8001
    mcp.run(transport="streamable-http")