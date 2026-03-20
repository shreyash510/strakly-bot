from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_client_notes(user_id: int, note_type: str = None) -> dict:
    """Get notes for a specific client.

    Args:
        user_id: The user ID of the client (required)
        note_type: Filter by type - general, medical, interaction, or follow_up (optional)

    Use this tool when user asks about:
    - Notes on a client
    - Client notes or comments
    - Medical notes for a client
    - Interaction history for a client
    """
    client = get_api_client()
    try:
        params = {"userId": user_id, "limit": 50}
        if note_type and note_type in ("general", "medical", "interaction", "follow_up"):
            params["noteType"] = note_type

        response = await client.get("/member-notes", params)
        notes = extract_list(response)

        if not notes:
            return {"count": 0, "notes": [], "message": "No notes found for this client."}

        return {
            "count": len(notes),
            "notes": [
                {
                    "id": n.get("id"),
                    "noteType": n.get("noteType"),
                    "content": n.get("content"),
                    "isPinned": n.get("isPinned"),
                    "visibility": n.get("visibility"),
                    "createdByName": n.get("createdByName"),
                    "createdAt": n.get("createdAt"),
                }
                for n in notes
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def create_client_note(user_id: int, content: str, note_type: str = "general", visibility: str = "all") -> dict:
    """Create a new note for a client.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        user_id: The user ID of the client (required)
        content: The note content (required)
        note_type: Type - general, medical, interaction, or follow_up (optional, default: general)
        visibility: Who can see - all, trainer_only, or admin_only (optional, default: all)
    """
    valid_types = ["general", "medical", "interaction", "follow_up"]
    if note_type not in valid_types:
        return {"error": f"Invalid note type. Must be one of: {', '.join(valid_types)}", "success": False}

    valid_visibility = ["all", "trainer_only", "admin_only"]
    if visibility not in valid_visibility:
        return {"error": f"Invalid visibility. Must be one of: {', '.join(valid_visibility)}", "success": False}

    client = get_api_client()
    try:
        data = {
            "userId": user_id,
            "content": content,
            "noteType": note_type,
            "visibility": visibility,
        }

        response = await client.post("/member-notes", data)
        return {
            "success": True,
            "message": f"Note created for client",
            "note": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def toggle_note_pin(note_id: int) -> dict:
    """Toggle pin/unpin a client note.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        note_id: The ID of the note to pin/unpin (required)
    """
    client = get_api_client()
    try:
        response = await client.patch(f"/member-notes/{note_id}/pin", {})
        return {
            "success": True,
            "message": "Note pin status toggled",
            "note": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}
