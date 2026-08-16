from langchain_core.tools import tool


@tool
def get_employee_count():
    """Get the current number of employees"""
    return "The Company currently has 100 employees"

@tool
def get_company_location():
    """Get the company location"""
    return "The Company is located in Mumbai."


@tool
def get_working_hours():
    """Get the company working hours"""
    return "The Company working hours are from 9AM to 6PM."