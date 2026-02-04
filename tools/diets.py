from langchain_core.tools import tool
from .base import get_api_client, get_current_branch_id


@tool
async def get_diet_plans() -> dict:
    """Get list of all diet plans.

    Use this tool when user asks about:
    - Diet plans
    - What diets do we have?
    - List diets
    - Our diet plans
    - Nutrition plans
    - Diet details
    """
    client = get_api_client()
    try:
        response = await client.get("/diets", {"limit": 20})
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_diet_by_id(diet_id: int) -> dict:
    """Get details of a specific diet plan by ID.

    Args:
        diet_id: The ID of the diet plan

    Use this tool when user asks about:
    - Details of a specific diet
    - Show me diet plan X
    """
    client = get_api_client()
    try:
        response = await client.get(f"/diets/{diet_id}")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_client_diet(client_id: int) -> dict:
    """Get diet plans assigned to a specific client.

    Args:
        client_id: The user ID of the client

    Use this tool when user asks about:
    - What diet is assigned to X?
    - Client's diet plan
    - Diet for a specific member
    """
    client = get_api_client()
    try:
        response = await client.get(f"/diets/user/{client_id}/assignments")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def create_diet(
    title: str,
    diet_type: str,
    category: str,
    content: str,
    description: str = None,
) -> dict:
    """Create a new diet plan.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        title: Name/title of the diet plan (required)
        diet_type: Type of diet - weight_loss, muscle_gain, maintenance, general (required)
        category: Category - veg, non_veg, vegan, keto, etc. (required)
        content: The diet plan content/meals (required)
        description: Brief description of the diet (optional)

    Returns:
        Success response with created diet details, or error message
    """
    client = get_api_client()
    try:
        data = {
            "title": title,
            "type": diet_type,
            "category": category,
            "content": content,
            "description": description or "",
            "status": "active",
        }

        # Add branch ID if available
        branch_id = get_current_branch_id()
        if branch_id:
            data["branchId"] = branch_id

        response = await client.post("/diets", data)

        return {
            "success": True,
            "message": f"Diet plan '{title}' created successfully",
            "diet": {
                "id": response.get("id"),
                "title": response.get("title"),
                "type": response.get("type"),
                "category": response.get("category"),
                "status": "active",
            },
        }
    except Exception as e:
        return {"error": str(e), "success": False}
