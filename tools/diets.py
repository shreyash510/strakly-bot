from langchain_core.tools import tool
from .base import get_api_client


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
