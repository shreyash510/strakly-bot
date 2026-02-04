from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_amenities_list() -> dict:
    """Get list of all amenities at the gym.

    Use this tool when user asks about:
    - Amenities
    - What amenities do we have?
    - List amenities
    - Our amenities
    - Gym amenities
    """
    client = get_api_client()
    try:
        response = await client.get("/amenities")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_facilities_list() -> dict:
    """Get list of all facilities at the gym.

    Use this tool when user asks about:
    - Facilities
    - What facilities do we have?
    - List facilities
    - Our facilities
    - Gym facilities
    - Equipment
    """
    client = get_api_client()
    try:
        response = await client.get("/facilities")
        return response
    except Exception as e:
        return {"error": str(e)}
