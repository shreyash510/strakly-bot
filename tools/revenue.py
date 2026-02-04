from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_revenue_stats(period: str = "month") -> dict:
    """Get revenue and financial statistics.

    Use this tool when user asks about:
    - Revenue this month/week/year
    - Income and expenses
    - Financial overview
    - Money earned

    Args:
        period: Time period - 'week', 'month', 'year' (default 'month')
    """
    client = get_api_client()
    try:
        response = await client.get("/reports/income-expense", {"period": period})
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_membership_sales(period: str = "month") -> dict:
    """Get membership sales statistics.

    Use this tool when user asks about:
    - Membership sales
    - Plans sold
    - Subscription revenue
    - Best selling plans

    Args:
        period: Time period - 'week', 'month', 'year' (default 'month')
    """
    client = get_api_client()
    try:
        response = await client.get("/reports/membership-sales", {"period": period})
        return response
    except Exception as e:
        return {"error": str(e)}
