from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_custom_fields(entity_type: str = None) -> dict:
    """Get custom field definitions configured for the gym.

    Args:
        entity_type: Filter by entity type - user, membership, lead (optional)

    Use this tool when user asks about:
    - Custom fields
    - What custom fields are configured
    - Custom field definitions
    """
    client = get_api_client()
    try:
        params = {"limit": 100}
        if entity_type and entity_type in ("user", "membership", "lead"):
            params["entityType"] = entity_type

        response = await client.get("/custom-fields", params)
        fields = extract_list(response)

        if not fields:
            return {"count": 0, "fields": [], "message": "No custom fields configured."}

        return {
            "count": len(fields),
            "fields": [
                {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "label": f.get("label"),
                    "fieldType": f.get("fieldType"),
                    "entityType": f.get("entityType"),
                    "isRequired": f.get("isRequired"),
                    "isActive": f.get("isActive"),
                    "options": f.get("options"),
                }
                for f in fields
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_entity_custom_values(entity_type: str, entity_id: int) -> dict:
    """Get custom field values for a specific entity (user, membership, etc.).

    Args:
        entity_type: The entity type - user, membership, lead (required)
        entity_id: The entity's ID (required)

    Use this tool when user asks about:
    - Custom field values for a member
    - What are the custom field values
    - Member's custom data
    """
    client = get_api_client()
    try:
        response = await client.get(f"/custom-fields/entity/{entity_type}/{entity_id}/values")
        values = extract_list(response)

        if not values:
            return {"count": 0, "values": [], "message": f"No custom field values for this {entity_type}."}

        return {
            "count": len(values),
            "values": [
                {
                    "fieldName": v.get("fieldName") or v.get("name"),
                    "fieldLabel": v.get("fieldLabel") or v.get("label"),
                    "value": v.get("value"),
                    "fieldType": v.get("fieldType"),
                }
                for v in values
            ],
        }
    except Exception as e:
        return {"error": str(e)}
