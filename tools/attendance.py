from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_attendance_today() -> dict:
    """Get today's attendance records including check-ins and check-outs.

    Use this tool when user asks about:
    - Today's attendance
    - Who checked in today?
    - How many people came today?
    - Today's check-ins list
    """
    client = get_api_client()
    try:
        response = await client.get("/attendance/today")
        records = extract_list(response)

        if len(records) == 0:
            return {
                "count": 0,
                "records": [],
                "message": "No attendance records for today. No one has checked in yet.",
            }

        return {
            "count": len(records),
            "records": [
                {
                    "id": r.get("id"),
                    "userName": r.get("userName"),
                    "checkInTime": r.get("checkInTime"),
                    "checkOutTime": r.get("checkOutTime"),
                    "status": r.get("status"),
                    "checkInMethod": r.get("checkInMethod"),
                }
                for r in records
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_attendance_stats() -> dict:
    """Get attendance statistics with today, this week, this month, and total counts.

    Use this tool when user asks about:
    - How many people came this week/month?
    - Attendance summary or overview
    - Weekly/monthly attendance count
    - Attendance this week
    - Attendance for this week
    - Monthly attendance summary
    """
    client = get_api_client()
    try:
        response = await client.get("/attendance/stats")

        if isinstance(response, dict):
            return {
                "todayPresent": response.get("todayPresent", 0),
                "thisWeekPresent": response.get("thisWeekPresent", 0),
                "thisMonthPresent": response.get("thisMonthPresent", 0),
                "totalPresent": response.get("totalPresent", 0),
            }

        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_attendance_reports(start_date: str = None, end_date: str = None) -> dict:
    """Get detailed attendance analytics report with trends, patterns, and top members.

    Args:
        start_date: Start date in YYYY-MM-DD format (optional, defaults to last 30 days)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)

    Use this tool when user asks about:
    - Attendance report
    - Attendance trends or analytics
    - Daily attendance trend
    - Weekly attendance pattern
    - Top attending members
    - Average daily attendance
    - Attendance gender distribution
    - Give me attendance report
    """
    client = get_api_client()
    try:
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        response = await client.get("/attendance/reports", params)

        if isinstance(response, dict):
            summary = response.get("summary", {})
            return {
                "summary": {
                    "totalCheckIns": summary.get("totalCheckIns", 0),
                    "avgDailyCheckIns": summary.get("avgDailyCheckIns", 0),
                    "uniqueMembers": summary.get("uniqueMembers", 0),
                    "avgDuration": summary.get("avgDuration", 0),
                },
                "dailyTrend": response.get("dailyTrend", []),
                "weeklyPattern": response.get("weeklyPattern", []),
                "genderDistribution": response.get("genderDistribution", {}),
                "topMembers": response.get("topMembers", []),
            }

        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_attendance_by_date(date: str) -> dict:
    """Get attendance records for a specific date.

    Args:
        date: Date in YYYY-MM-DD format

    Use this tool when user asks about:
    - Attendance on a specific date
    - Who came on Monday/Tuesday/etc.
    - Attendance on 2025-01-15
    - How many people came yesterday
    """
    client = get_api_client()
    try:
        response = await client.get(f"/attendance/date/{date}")
        records = extract_list(response)

        if len(records) == 0:
            return {
                "count": 0,
                "date": date,
                "records": [],
                "message": f"No attendance records found for {date}.",
            }

        return {
            "count": len(records),
            "date": date,
            "records": [
                {
                    "id": r.get("id"),
                    "userName": r.get("userName"),
                    "checkInTime": r.get("checkInTime"),
                    "checkOutTime": r.get("checkOutTime"),
                    "status": r.get("status"),
                }
                for r in records
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_all_attendance(start_date: str = None, end_date: str = None, page: int = 1) -> dict:
    """Get paginated attendance history with optional date range filter.

    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        page: Page number (default 1)

    Use this tool when user asks about:
    - All attendance records
    - Attendance history
    - Attendance list for a date range
    - Show me attendance records from last week
    """
    client = get_api_client()
    try:
        params = {"page": page, "limit": 50}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        response = await client.get("/attendance/all", params)

        if isinstance(response, dict):
            records = response.get("records", [])
            return {
                "total": response.get("total", 0),
                "page": response.get("page", 1),
                "pages": response.get("pages", 1),
                "records": [
                    {
                        "id": r.get("id"),
                        "userName": r.get("userName"),
                        "checkInTime": r.get("checkInTime"),
                        "checkOutTime": r.get("checkOutTime"),
                        "date": r.get("date"),
                        "status": r.get("status"),
                    }
                    for r in records
                ],
            }

        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_present_count() -> dict:
    """Get the count of people currently present (checked-in) at the gym right now.

    Use this tool when user asks about:
    - How many people are in the gym right now?
    - Current gym occupancy
    - Who is currently present?
    - Currently checked in count
    """
    client = get_api_client()
    try:
        response = await client.get("/attendance/present-count")

        if isinstance(response, dict):
            return {
                "currentlyPresent": response.get("count", 0),
                "message": f"{response.get('count', 0)} member(s) currently present in the gym.",
            }

        return response
    except Exception as e:
        return {"error": str(e)}
