from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_revenue_stats() -> dict:
    """Get revenue and financial statistics for current month.

    Use this tool when user asks about:
    - Revenue this month
    - Income and expenses
    - Financial overview
    - Money earned
    """
    client = get_api_client()
    try:
        response = await client.get("/reports/income-expense")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_membership_sales() -> dict:
    """Get membership sales statistics for current month.

    Use this tool when user asks about:
    - Membership sales
    - Plans sold
    - Subscription revenue
    - Best selling plans
    """
    client = get_api_client()
    try:
        response = await client.get("/reports/membership-sales")
        return response
    except Exception as e:
        return {"error": str(e)}
