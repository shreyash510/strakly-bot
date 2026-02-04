from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_enquiries_list(status: str = None, limit: int = 10) -> dict:
    """Get list of enquiries/leads.

    Use this tool when user asks about:
    - Enquiries or leads
    - Pending enquiries
    - New leads
    - Follow-ups needed

    Args:
        status: Filter by status (pending, contacted, converted, closed)
        limit: Maximum number of results (default 10)
    """
    client = get_api_client()
    params = {"limit": limit}
    if status:
        params["status"] = status

    try:
        response = await client.get("/enquiries", params)
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_enquiries_stats() -> dict:
    """Get statistics about enquiries/leads.

    Use this tool when user asks about:
    - Enquiry statistics
    - Conversion rate
    - Lead pipeline
    - Total enquiries
    """
    client = get_api_client()
    try:
        response = await client.get("/enquiries/stats")
        return response
    except Exception as e:
        return {"error": str(e)}
