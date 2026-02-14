from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_currencies() -> dict:
    """Get all active currencies configured for the gym.

    Use this tool when user asks about:
    - Available currencies
    - Supported currencies
    - Currency list
    """
    client = get_api_client()
    try:
        response = await client.get("/currencies")
        currencies = extract_list(response)

        if not currencies:
            return {"count": 0, "currencies": [], "message": "No currencies configured."}

        return {
            "count": len(currencies),
            "currencies": [
                {
                    "id": c.get("id"),
                    "code": c.get("code"),
                    "name": c.get("name"),
                    "symbol": c.get("symbol"),
                    "decimalPlaces": c.get("decimalPlaces"),
                    "isActive": c.get("isActive"),
                }
                for c in currencies
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def convert_currency(from_code: str, to_code: str, amount: float) -> dict:
    """Convert an amount from one currency to another.

    Args:
        from_code: Source currency code e.g. USD, INR, EUR (required)
        to_code: Target currency code e.g. USD, INR, EUR (required)
        amount: Amount to convert (required)

    Use this tool when user asks about:
    - Currency conversion
    - Convert amount between currencies
    - How much is X in Y currency
    - Exchange rate
    """
    client = get_api_client()
    try:
        response = await client.get("/currencies/convert", {
            "from": from_code,
            "to": to_code,
            "amount": amount,
        })
        return response
    except Exception as e:
        return {"error": str(e)}
