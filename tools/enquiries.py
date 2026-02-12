from langchain_core.tools import tool
from .base import get_api_client, get_current_branch_id, generate_password, extract_list


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
        response = await client.get("/users", {"role": "client", "status": "onboarding", "noPagination": "true"})

        enquiries = extract_list(response)

        if len(enquiries) == 0:
            return {
                "count": 0,
                "enquiries": [],
                "message": "No enquiries found."
            }

        return {
            "count": len(enquiries),
            "enquiries": [{"id": e.get("id"), "name": e.get("name"), "email": e.get("email"), "status": e.get("status")} for e in enquiries],
        }
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
        # Extract only enquiry/lead-relevant fields to avoid returning the entire dashboard
        enquiry_keys = [k for k in response if any(term in k.lower() for term in ("enquir", "lead", "onboarding", "pending", "inquiry"))]
        stats = {k: response[k] for k in enquiry_keys if k in response}
        if not stats:
            # Fallback: return full response if no enquiry-specific keys found
            return response
        return stats
    except Exception as e:
        return {"error": str(e)}


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
            data["branchId"] = branch_id

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


@tool
async def bulk_create_enquiries(
    enquiries_json: str,
) -> dict:
    """Bulk create multiple enquiries/leads at once.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        enquiries_json: JSON string containing array of enquiry objects.
            Each object should have: name (required), email (required),
            and optionally: phone, gender, address, city.
            Example: '[{"name": "John", "email": "john@example.com", "phone": "1234567890"}, {"name": "Jane", "email": "jane@example.com"}]'

    Returns:
        Summary with success count, failed count, errors, and created enquiries list.
    """
    import json as json_module

    client = get_api_client()
    try:
        enquiries = json_module.loads(enquiries_json)

        if not isinstance(enquiries, list):
            return {"error": "Expected a JSON array of enquiry objects", "success": False}

        if len(enquiries) == 0:
            return {"error": "No enquiries provided", "success": False}

        if len(enquiries) > 50:
            return {"error": "Maximum 50 enquiries allowed per batch", "success": False}

        # Prepare each enquiry with required fields
        users = []
        for i, enq in enumerate(enquiries):
            if not enq.get("name") or not enq.get("email"):
                return {
                    "error": f"Enquiry {i + 1}: name and email are required",
                    "success": False,
                }

            user_data = {
                "name": enq["name"],
                "email": enq["email"],
                "password": generate_password(),
                "status": "onboarding",
                "role": "client",
            }

            if enq.get("phone"):
                user_data["phone"] = enq["phone"]
            if enq.get("gender") and enq["gender"] in ["male", "female", "other"]:
                user_data["gender"] = enq["gender"]
            if enq.get("address"):
                user_data["address"] = enq["address"]
            if enq.get("city"):
                user_data["city"] = enq["city"]

            branch_id = get_current_branch_id()
            if branch_id:
                user_data["branchId"] = branch_id

            users.append(user_data)

        # Call bulk create endpoint
        response = await client.post("/users/bulk/create", {"users": users})

        total_submitted = len(enquiries)
        total_created = response.get("success", 0)
        total_failed = response.get("failed", 0)

        return {
            "success": True,
            "message": f"Bulk enquiry creation completed: {total_created} created, {total_failed} failed out of {total_submitted} submitted",
            "total_submitted": total_submitted,
            "total_created": total_created,
            "total_failed": total_failed,
            "created": response.get("created", []),
            "errors": response.get("errors", []),
        }
    except json_module.JSONDecodeError:
        return {"error": "Invalid JSON format. Please provide a valid JSON array.", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}
