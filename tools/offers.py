from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_offers_list() -> dict:
    """Get list of all offers.

    Use this tool when user asks about:
    - Offers
    - What offers do we have?
    - Current offers
    - Our offers
    - Discounts
    - Promotions
    """
    client = get_api_client()
    try:
        response = await client.get("/offers")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_active_offers() -> dict:
    """Get list of currently active offers.

    Use this tool when user asks about:
    - Active offers
    - Current running offers
    - Live offers
    - Ongoing promotions
    """
    client = get_api_client()
    try:
        response = await client.get("/offers/active")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_offer_details(offer_id: int) -> dict:
    """Get details of a specific offer.

    Args:
        offer_id: The ID of the offer

    Use this tool when user asks about:
    - Details of a specific offer
    - Show me offer X
    """
    client = get_api_client()
    try:
        response = await client.get(f"/offers/{offer_id}")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def validate_offer_code(code: str) -> dict:
    """Validate an offer/promo code.

    Args:
        code: The offer code to validate

    Use this tool when user asks about:
    - Is this code valid?
    - Check promo code
    - Validate offer code
    """
    client = get_api_client()
    try:
        response = await client.get(f"/offers/validate/{code}")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def create_offer(
    name: str,
    discount_percentage: int,
    start_date: str,
    end_date: str,
    code: str = None,
    description: str = None,
) -> dict:
    """Create a new discount offer/promotion.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Name of the offer (required)
        discount_percentage: Discount percentage, e.g., 10, 20, 50 (required)
        start_date: Start date in YYYY-MM-DD format (required)
        end_date: End date in YYYY-MM-DD format (required)
        code: Offer code like "NEWYEAR20" (optional, auto-generated if not provided)
        description: Description of the offer (optional)

    Returns:
        Success response with created offer details, or error message
    """
    client = get_api_client()
    try:
        # Generate code from name if not provided
        offer_code = code or name.upper().replace(" ", "")

        data = {
            "code": offer_code,
            "name": name,
            "description": description or "",
            "discountType": "percentage",
            "discountValue": discount_percentage,
            "validFrom": start_date,
            "validTo": end_date,
            "applicableToAll": True,
            "isActive": True,
        }

        response = await client.post("/offers", data)

        return {
            "success": True,
            "message": f"Offer '{name}' created successfully",
            "offer": {
                "id": response.get("id"),
                "name": response.get("name"),
                "code": response.get("code"),
                "discount": f"{discount_percentage}%",
                "validFrom": start_date,
                "validTo": end_date,
            },
        }
    except Exception as e:
        return {"error": str(e), "success": False}
