from langchain_core.tools import tool
from .base import get_api_client, get_current_branch_id
import secrets
import string


@tool
async def get_enquiries_list() -> dict:
    """Get list of enquiries/leads (users with onboarding/pending status).

    Use this tool when user asks about:
    - Enquiries or leads
    - Pending enquiries
    - New leads
    - Follow-ups needed
    """
    client = get_api_client()
    try:
        response = await client.get("/dashboard/admin/new-inquiries", {"limit": 10})
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_enquiries_stats() -> dict:
    """Get statistics about enquiries/leads.

    Use this tool when user asks about:
    - Enquiry statistics
    - Conversion rate
    - Lead pipeline
    - Total enquiries
    """
    client = get_api_client()
    try:
        # Dashboard includes enquiry stats
        response = await client.get("/dashboard/admin")
        return response
    except Exception as e:
        return {"error": str(e)}


def generate_password(length: int = 12) -> str:
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@tool
async def create_enquiry(
    name: str,
    email: str,
    phone: str = None,
    gender: str = None,
    address: str = None,
    city: str = None,
) -> dict:
    """Create a new enquiry/lead with the provided details.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Full name of the person (required)
        email: Email address (required)
        phone: Phone number (optional)
        gender: Gender - male, female, or other (optional)
        address: Address (optional)
        city: City (optional)

    Returns:
        Success response with created enquiry details, or error message
    """
    client = get_api_client()
    try:
        # Generate a temporary password for the enquiry
        temp_password = generate_password()

        # Prepare the data
        data = {
            "name": name,
            "email": email,
            "password": temp_password,
            "status": "onboarding",
            "role": "client",
        }

        # Add optional fields if provided
        if phone:
            data["phone"] = phone
        if gender and gender in ["male", "female", "other"]:
            data["gender"] = gender
        if address:
            data["address"] = address
        if city:
            data["city"] = city

        # Add branch ID if available from context
        branch_id = get_current_branch_id()
        if branch_id:
            data["branchIds"] = [branch_id]

        # Create the user via POST /users
        response = await client.post("/users", data)

        return {
            "success": True,
            "message": f"Enquiry created successfully for {name}",
            "enquiry": {
                "id": response.get("id"),
                "name": response.get("name"),
                "email": response.get("email"),
                "phone": response.get("phone"),
                "status": "onboarding",
            },
            "temp_password": temp_password,
        }
    except Exception as e:
        return {"error": str(e), "success": False}
