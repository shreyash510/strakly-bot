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


@tool
async def create_plan(
    name: str,
    price: float,
    duration: int,
    description: str = None,
    features: str = None,
) -> dict:
    """Create a new membership plan.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Name of the plan (required)
        price: Price in INR (required)
        duration: Duration in days (required)
        description: Description of the plan (optional)
        features: Comma-separated features like "Personal trainer, Diet plan, Locker" (optional)

    Returns:
        Success response with created plan details, or error message
    """
    client = get_api_client()
    try:
        # Generate code from name
        code = name.lower().replace(" ", "-")

        data = {
            "code": code,
            "name": name,
            "price": price,
            "durationValue": duration,
            "durationType": "day",
            "description": description or "",
            "features": features.split(",") if features else [],
        }

        response = await client.post("/plans", data)

        return {
            "success": True,
            "message": f"Plan '{name}' created successfully",
            "plan": {
                "id": response.get("id"),
                "name": response.get("name"),
                "price": response.get("price"),
                "duration": duration,
                "description": response.get("description"),
            },
        }
    except Exception as e:
        return {"error": str(e), "success": False}
