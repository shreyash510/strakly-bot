from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_membership_plans() -> dict:
    """Get list of all membership plans.

    Use this tool when user asks about:
    - Plans
    - Membership plans
    - What plans do we have?
    - Current plans
    - Our plans
    - Pricing plans
    - Subscription plans
    """
    client = get_api_client()
    try:
        response = await client.get("/plans")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_featured_plans() -> dict:
    """Get list of featured/popular membership plans.

    Use this tool when user asks about:
    - Featured plans
    - Popular plans
    - Best plans
    - Recommended plans
    """
    client = get_api_client()
    try:
        response = await client.get("/plans/featured")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_plan_details(plan_id: int) -> dict:
    """Get details of a specific membership plan.

    Args:
        plan_id: The ID of the plan

    Use this tool when user asks about:
    - Details of a specific plan
    - Show me plan X
    """
    client = get_api_client()
    try:
        response = await client.get(f"/plans/{plan_id}")
        return response
    except Exception as e:
        return {"error": str(e)}
