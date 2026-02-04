from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_staff_salary(staff_id: int) -> dict:
    """Get salary details for a specific staff member.

    Args:
        staff_id: The user ID of the staff member

    Use this tool when user asks about:
    - Salary of a specific staff member
    - How much does X earn?
    - Salary details of manager/trainer
    - Payment history of staff
    - Staff salary information
    """
    client = get_api_client()
    try:
        response = await client.get("/salary", {"staffId": staff_id, "limit": 12})
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_salary_stats() -> dict:
    """Get salary statistics including total paid, pending, etc.

    Use this tool when user asks about:
    - Total salary expenses
    - How much salary is pending?
    - Salary statistics
    - Overall salary summary
    """
    client = get_api_client()
    try:
        response = await client.get("/salary/stats")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_pending_salaries() -> dict:
    """Get list of pending/unpaid salaries.

    Use this tool when user asks about:
    - Unpaid salaries
    - Pending salary payments
    - Who hasn't been paid?
    - Outstanding salaries
    """
    client = get_api_client()
    try:
        response = await client.get("/salary", {"paymentStatus": "pending", "limit": 20})
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_all_salaries() -> dict:
    """Get all salary records.

    Use this tool when user asks about:
    - All salaries
    - List of salary payments
    - Salary history
    - Show all salary records
    """
    client = get_api_client()
    try:
        response = await client.get("/salary", {"limit": 20})
        return response
    except Exception as e:
        return {"error": str(e)}
