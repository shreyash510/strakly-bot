from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_member_photos(user_id: int, category: str = None) -> dict:
    """Get progress photos for a specific member.

    Args:
        user_id: The user ID of the member (required)
        category: Filter by category - front, side, back, or other (optional)

    Use this tool when user asks about:
    - Member's progress photos
    - Show me photos for a member
    - Progress tracking photos
    """
    client = get_api_client()
    try:
        params = {}
        if category and category in ("front", "side", "back", "other"):
            params["category"] = category

        response = await client.get(f"/progress-photos/user/{user_id}", params)
        photos = extract_list(response)

        if not photos:
            return {"count": 0, "photos": [], "message": "No progress photos found for this member."}

        return {
            "count": len(photos),
            "photos": [
                {
                    "id": p.get("id"),
                    "category": p.get("category"),
                    "takenAt": p.get("takenAt"),
                    "notes": p.get("notes"),
                    "uploadedByName": p.get("uploadedByName"),
                    "photoUrl": p.get("photoUrl"),
                }
                for p in photos
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_photo_details(photo_id: int) -> dict:
    """Get details of a specific progress photo.

    Args:
        photo_id: The ID of the photo

    Use this tool when user asks about a specific photo's details.
    """
    client = get_api_client()
    try:
        response = await client.get(f"/progress-photos/{photo_id}")
        return response
    except Exception as e:
        return {"error": str(e)}
