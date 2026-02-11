from langchain_core.tools import tool
from .base import get_api_client, extract_list, get_current_branch_id


@tool
async def get_salary_by_name(search: str) -> dict:
    """Get salary details for a staff member by searching their name.

    Args:
        search: Staff member name to search for

    Use this tool when user asks about:
    - Salary of a specific person by name
    - How much does [name] earn?
    - Salary details of [name]
    - [name]'s salary
    """
    client = get_api_client()
    try:
        # First search for the staff member in managers
        managers = await client.get("/users", {"role": "manager", "search": search, "noPagination": "true"})
        trainers = await client.get("/users", {"role": "trainer", "search": search, "noPagination": "true"})
        branch_admins = await client.get("/users", {"role": "branch_admin", "search": search, "noPagination": "true"})

        # Find the staff member
        staff = None
        staff_role = None

        for role, data in [("manager", managers), ("trainer", trainers), ("branch_admin", branch_admins)]:
            items = extract_list(data)
            if items:
                staff = items[0]
                staff_role = role
                break

        if not staff:
            return {"error": f"No staff member found matching '{search}'"}

        staff_id = staff.get("id")
        staff_name = staff.get("name")

        # Get salary records for this staff member
        salary_response = await client.get("/salary", {"staffId": staff_id, "limit": 12})

        salary_data = extract_list(salary_response)

        if not salary_data or len(salary_data) == 0:
            return {
                "staff": {
                    "id": staff_id,
                    "name": staff_name,
                    "role": staff_role
                },
                "message": f"No salary records found for {staff_name}",
                "salaryRecords": []
            }

        return {
            "staff": {
                "id": staff_id,
                "name": staff_name,
                "role": staff_role
            },
            "salaryRecords": salary_data,
            "totalRecords": len(salary_data)
        }
    except Exception as e:
        return {"error": str(e)}


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
async def create_salary(
    staff_id: int,
    month: int,
    year: int,
    base_salary: float,
    bonus: float = 0,
    deductions: float = 0,
    notes: str = None,
    is_recurring: bool = False,
) -> dict:
    """Create a new salary record for a staff member.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        staff_id: The user ID of the staff member (required)
        month: Month number 1-12 (required)
        year: Year e.g. 2026 (required)
        base_salary: Base salary amount in INR (required)
        bonus: Bonus amount in INR (optional, default 0)
        deductions: Deductions amount in INR (optional, default 0)
        notes: Any notes for the salary record (optional)
        is_recurring: Whether to auto-generate next month (optional, default False)

    Returns:
        Success response with created salary details, or error message
    """
    client = get_api_client()
    try:
        data = {
            "staffId": staff_id,
            "month": month,
            "year": year,
            "baseSalary": base_salary,
            "bonus": bonus,
            "deductions": deductions,
            "isRecurring": is_recurring,
        }
        if notes:
            data["notes"] = notes

        response = await client.post("/salary", data)

        net_amount = base_salary + bonus - deductions
        return {
            "success": True,
            "message": f"Salary record created successfully for month {month}/{year}",
            "salary": {
                "id": response.get("id"),
                "staffId": staff_id,
                "month": month,
                "year": year,
                "baseSalary": base_salary,
                "bonus": bonus,
                "deductions": deductions,
                "netAmount": net_amount,
                "isRecurring": is_recurring,
                "paymentStatus": "pending",
            },
        }
    except Exception as e:
        return {"error": str(e), "success": False}


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
