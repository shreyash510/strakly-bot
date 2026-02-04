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
