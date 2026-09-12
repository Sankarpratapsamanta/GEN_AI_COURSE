from langchain_core.tools import tool


@tool
def get_employee_count():
    """Get the total number of employees in the company

    This tool does not require any arguments.
    """
    return "The Company currently has 100 employees"

@tool
def get_company_location():
    """Get the company location
    This tool does not require any arguments.
    """
    return "The Company is located in Mumbai."


@tool
def get_working_hours():
    """Get the company working hours
    This tool does not require any arguments.
    """
    return "The Company working hours are from 9AM to 6PM."