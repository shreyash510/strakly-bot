from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_guest_visits(date_from: str = None, date_to: str = None) -> dict:
    """Get guest/day-pass visits with optional date filters.

    Args:
        date_from: Start date filter in YYYY-MM-DD format (optional)
        date_to: End date filter in YYYY-MM-DD format (optional)

    Use this tool when user asks about:
    - Guest visits
    - Day pass visitors
    - Who visited as a guest
    - Guest list
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to

        response = await client.get("/guest-visits", params)
        visits = extract_list(response)

        if not visits:
            return {"count": 0, "visits": [], "message": "No guest visits found."}

        return {
            "count": len(visits),
            "visits": [
                {
                    "id": v.get("id"),
                    "guestName": v.get("guestName"),
                    "guestPhone": v.get("guestPhone"),
                    "guestEmail": v.get("guestEmail"),
                    "broughtByName": v.get("broughtByName"),
                    "visitDate": v.get("visitDate"),
                    "dayPassAmount": v.get("dayPassAmount"),
                    "convertedToMember": v.get("convertedToMember"),
                }
                for v in visits
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_guest_visit_stats() -> dict:
    """Get guest visit statistics.

    Use this tool when user asks about:
    - Guest visit stats
    - How many guests visited
    - Guest conversion rate
    - Day pass statistics
    """
    client = get_api_client()
    try:
        response = await client.get("/guest-visits/stats")
        return response
    except Exception as e:
        return {"error": str(e)}
