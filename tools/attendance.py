from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_attendance_today() -> dict:
    """Get today's attendance records including check-ins and check-outs.

    Use this tool when user asks about:
    - Today's attendance
    - Who checked in today?
    - How many people came today?
    - Current gym occupancy
    """
    client = get_api_client()
    try:
        response = await client.get("/attendance/today")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_attendance_stats(period: str = "week") -> dict:
    """Get attendance statistics for a given period.

    Use this tool when user asks about:
    - Attendance trends
    - Weekly/monthly attendance
    - Peak hours
    - Average daily attendance

    Args:
        period: Time period - 'today', 'week', 'month' (default 'week')
    """
    client = get_api_client()
    try:
        response = await client.get("/attendance/stats", {"period": period})
        return response
    except Exception as e:
        return {"error": str(e)}
