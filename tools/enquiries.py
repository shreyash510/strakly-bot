from langchain_core.tools import tool
from .base import get_api_client


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
