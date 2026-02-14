from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_equipment(status: str = None) -> dict:
    """Get gym equipment list with optional status filter.

    Args:
        status: Filter by status - in_service, under_repair, retired (optional)

    Use this tool when user asks about:
    - Equipment list
    - Gym machines
    - Equipment inventory
    - What equipment is available
    - Broken or under repair equipment
    """
    client = get_api_client()
    try:
        params = {"limit": 100}
        if status and status in ("in_service", "under_repair", "retired"):
            params["status"] = status

        response = await client.get("/equipment", params)
        items = extract_list(response)

        if not items:
            return {"count": 0, "equipment": [], "message": "No equipment found."}

        return {
            "count": len(items),
            "equipment": [
                {
                    "id": e.get("id"),
                    "name": e.get("name"),
                    "brand": e.get("brand"),
                    "model": e.get("model"),
                    "status": e.get("status"),
                    "location": e.get("location"),
                    "warrantyExpiry": e.get("warrantyExpiry"),
                }
                for e in items
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_equipment_stats() -> dict:
    """Get equipment statistics including counts by status and maintenance info.

    Use this tool when user asks about:
    - Equipment stats
    - How many machines
    - Equipment status overview
    - Maintenance summary
    """
    client = get_api_client()
    try:
        response = await client.get("/equipment/stats")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_upcoming_maintenance() -> dict:
    """Get upcoming equipment maintenance tasks.

    Use this tool when user asks about:
    - Upcoming maintenance
    - Scheduled maintenance
    - Equipment maintenance due
    - What needs servicing
    """
    client = get_api_client()
    try:
        response = await client.get("/equipment/maintenance/upcoming")
        items = extract_list(response)

        if not items:
            return {"count": 0, "maintenance": [], "message": "No upcoming maintenance tasks."}

        return {
            "count": len(items),
            "maintenance": [
                {
                    "id": m.get("id"),
                    "equipmentName": m.get("equipmentName"),
                    "type": m.get("type"),
                    "description": m.get("description"),
                    "scheduledDate": m.get("scheduledDate"),
                    "status": m.get("status"),
                }
                for m in items
            ],
        }
    except Exception as e:
        return {"error": str(e)}
