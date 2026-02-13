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


@tool
async def create_amenity(
    name: str,
    description: str = None,
) -> dict:
    """Create a new amenity (e.g., Parking, Locker, Shower, WiFi).

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Name of the amenity (required)
        description: Description of the amenity (optional)

    Returns:
        Success response with created amenity details, or error message
    """
    client = get_api_client()
    try:
        # Generate code from name
        code = name.upper().replace(" ", "_")

        data = {
            "name": name,
            "code": code,
            "isActive": True,
        }

        if description:
            data["description"] = description

        response = await client.post("/amenities", data)

        return {
            "success": True,
            "message": f"Amenity '{name}' created successfully",
            "amenity": {
                "id": response.get("id"),
                "name": response.get("name"),
                "code": response.get("code"),
                "description": response.get("description"),
            },
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def create_facility(
    name: str,
    description: str = None,
) -> dict:
    """Create a new facility (e.g., Cardio Zone, Weight Area, Yoga Room, Swimming Pool).

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Name of the facility (required)
        description: Description of the facility (optional)

    Returns:
        Success response with created facility details, or error message
    """
    client = get_api_client()
    try:
        # Generate code from name
        code = name.upper().replace(" ", "_")

        data = {
            "name": name,
            "code": code,
            "isActive": True,
        }

        if description:
            data["description"] = description

        response = await client.post("/facilities", data)

        return {
            "success": True,
            "message": f"Facility '{name}' created successfully",
            "facility": {
                "id": response.get("id"),
                "name": response.get("name"),
                "code": response.get("code"),
                "description": response.get("description"),
            },
        }
    except Exception as e:
        return {"error": str(e), "success": False}
