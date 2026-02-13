from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_class_types() -> dict:
    """Get all class/group types offered by the gym.

    Use this tool when user asks about:
    - What classes are available
    - Class types offered
    - Group fitness options
    - Types of classes (yoga, HIIT, spin, etc.)
    """
    client = get_api_client()
    try:
        response = await client.get("/classes/types", {"limit": 100})
        types = extract_list(response)

        if not types:
            return {"count": 0, "classTypes": [], "message": "No class types found."}

        return {
            "count": len(types),
            "classTypes": [
                {
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "category": t.get("category"),
                    "defaultDuration": t.get("defaultDuration"),
                    "defaultCapacity": t.get("defaultCapacity"),
                    "description": t.get("description"),
                }
                for t in types
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_class_sessions(from_date: str = None, to_date: str = None, status: str = None) -> dict:
    """Get scheduled class sessions with optional date and status filters.

    Args:
        from_date: Start date filter in YYYY-MM-DD format (optional)
        to_date: End date filter in YYYY-MM-DD format (optional)
        status: Filter by status - scheduled, cancelled, or completed (optional)

    Use this tool when user asks about:
    - Upcoming classes
    - Class schedule for a date
    - Today's classes
    - Cancelled classes
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if status and status in ("scheduled", "cancelled", "completed"):
            params["status"] = status

        response = await client.get("/classes/sessions", params)
        sessions = extract_list(response)

        if not sessions:
            return {"count": 0, "sessions": [], "message": "No class sessions found."}

        return {
            "count": len(sessions),
            "sessions": [
                {
                    "id": s.get("id"),
                    "className": s.get("classTypeName") or s.get("className"),
                    "instructorName": s.get("instructorName"),
                    "date": s.get("date"),
                    "startTime": s.get("startTime"),
                    "endTime": s.get("endTime"),
                    "status": s.get("status"),
                    "capacity": s.get("capacity"),
                    "bookedCount": s.get("bookedCount"),
                }
                for s in sessions
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_session_bookings(session_id: int) -> dict:
    """Get bookings for a specific class session.

    Args:
        session_id: The class session ID (required)

    Use this tool when user asks about:
    - Who is booked for a class
    - Class attendance list
    - Bookings for a session
    """
    client = get_api_client()
    try:
        response = await client.get(f"/classes/sessions/{session_id}/bookings")
        bookings = extract_list(response)

        if not bookings:
            return {"count": 0, "bookings": [], "message": "No bookings for this session."}

        return {
            "count": len(bookings),
            "bookings": [
                {
                    "id": b.get("id"),
                    "userName": b.get("userName"),
                    "userId": b.get("userId"),
                    "status": b.get("status"),
                    "bookedAt": b.get("bookedAt"),
                }
                for b in bookings
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_my_class_bookings() -> dict:
    """Get the current user's class bookings.

    Use this tool when user asks about:
    - My booked classes
    - My class schedule
    - What classes am I signed up for
    """
    client = get_api_client()
    try:
        response = await client.get("/classes/my-bookings")
        bookings = extract_list(response)

        if not bookings:
            return {"count": 0, "bookings": [], "message": "You have no class bookings."}

        return {
            "count": len(bookings),
            "bookings": [
                {
                    "id": b.get("id"),
                    "className": b.get("className"),
                    "date": b.get("date"),
                    "startTime": b.get("startTime"),
                    "status": b.get("status"),
                    "instructorName": b.get("instructorName"),
                }
                for b in bookings
            ],
        }
    except Exception as e:
        return {"error": str(e)}
