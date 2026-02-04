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
async def get_attendance_stats() -> dict:
    """Get attendance statistics.

    Use this tool when user asks about:
    - Attendance trends
    - Weekly/monthly attendance
    - Peak hours
    - Average daily attendance
    """
    client = get_api_client()
    try:
        response = await client.get("/attendance/stats")
        return response
    except Exception as e:
        return {"error": str(e)}
