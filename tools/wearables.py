from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_wearable_connections() -> dict:
    """Get the current user's connected wearable devices.

    Use this tool when user asks about:
    - My connected wearables
    - My fitness trackers
    - Which devices are connected
    - Wearable connection status
    """
    client = get_api_client()
    try:
        response = await client.get("/wearables/connections/me")
        connections = extract_list(response)

        if not connections:
            return {"count": 0, "connections": [], "message": "No wearable devices connected."}

        return {
            "count": len(connections),
            "connections": [
                {
                    "id": c.get("id"),
                    "provider": c.get("provider"),
                    "isActive": c.get("isActive"),
                    "lastSyncedAt": c.get("lastSyncedAt"),
                    "syncError": c.get("syncError"),
                }
                for c in connections
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_wearable_summary() -> dict:
    """Get today's wearable health data summary (steps, heart rate, calories, sleep, etc.).

    Use this tool when user asks about:
    - My health data today
    - Today's steps or heart rate
    - My fitness summary
    - Daily wearable stats
    """
    client = get_api_client()
    try:
        response = await client.get("/wearables/data/me/summary")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_user_wearable_data(user_id: int, data_type: str = None) -> dict:
    """Get wearable health data for a specific user (admin view).

    Args:
        user_id: The user ID (required)
        data_type: Filter by data type - steps, heart_rate, calories_burned, sleep_hours, active_minutes, distance_km (optional)

    Use this tool when user asks about:
    - A member's health data
    - Wearable data for a user
    - Member's step count or heart rate
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if data_type:
            params["dataType"] = data_type

        response = await client.get(f"/wearables/data/user/{user_id}", params)
        data = extract_list(response)

        if not data:
            return {"count": 0, "data": [], "message": "No wearable data found for this user."}

        return {
            "count": len(data),
            "data": [
                {
                    "id": d.get("id"),
                    "dataType": d.get("dataType"),
                    "value": d.get("value"),
                    "unit": d.get("unit"),
                    "provider": d.get("provider"),
                    "recordedDate": d.get("recordedDate"),
                }
                for d in data
            ],
        }
    except Exception as e:
        return {"error": str(e)}
