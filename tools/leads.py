from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_leads_list() -> dict:
    """Get list of all leads/prospects in the CRM pipeline.

    Use this tool when user asks about:
    - List of leads
    - Show me all leads/prospects
    - Who are my prospects
    """
    client = get_api_client()
    try:
        response = await client.get("/leads", {"limit": 100})
        leads = extract_list(response)

        if not leads:
            return {"count": 0, "leads": [], "message": "No leads found."}

        return {
            "count": len(leads),
            "leads": [
                {
                    "id": l.get("id"),
                    "name": l.get("name"),
                    "email": l.get("email"),
                    "phone": l.get("phone"),
                    "stage": l.get("pipelineStage"),
                    "score": l.get("score"),
                    "source": l.get("leadSource"),
                    "assignedTo": l.get("assignedToName"),
                    "dealValue": l.get("dealValue"),
                }
                for l in leads
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_leads_stats(date_from: str = None, date_to: str = None) -> dict:
    """Get lead pipeline statistics (totals by stage, score, conversion rate, by source, by staff).

    Args:
        date_from: Filter stats from this date (YYYY-MM-DD format, optional)
        date_to: Filter stats to this date (YYYY-MM-DD format, optional)

    Use this tool when user asks about:
    - Lead stats/statistics
    - Pipeline overview
    - How many leads do we have
    - Conversion rate
    - Leads by source
    - Conversion by staff
    - Average days in stage
    """
    client = get_api_client()
    try:
        params = {}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to

        response = await client.get("/leads/stats", params)
        return {
            "total": response.get("total", 0),
            "byStage": response.get("byStage", {}),
            "byScore": response.get("byScore", {}),
            "conversionRate": response.get("conversionRate", 0),
            "bySource": response.get("bySource", []),
            "conversionBySource": response.get("conversionBySource", []),
            "conversionByStaff": response.get("conversionByStaff", []),
            "avgDaysInStage": response.get("avgDaysInStage", {}),
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_lead_stage_history(lead_id: int) -> dict:
    """Get the stage change history for a lead (when it moved between pipeline stages).

    Args:
        lead_id: The ID of the lead

    Use this tool when user asks about:
    - Lead stage history
    - When did this lead move stages
    - How long was this lead in a stage
    """
    client = get_api_client()
    try:
        response = await client.get(f"/leads/{lead_id}/stage-history")
        history = extract_list(response)
        return {"count": len(history), "history": history}
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_lead_details(lead_id: int) -> dict:
    """Get full details of a specific lead by ID.

    Args:
        lead_id: The ID of the lead

    Use this tool when user asks about a specific lead's details.
    """
    client = get_api_client()
    try:
        response = await client.get(f"/leads/{lead_id}")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def create_lead(
    name: str,
    email: str = None,
    phone: str = None,
    lead_source: str = None,
    score: str = None,
    notes: str = None,
    deal_value: float = None,
) -> dict:
    """Create a new lead/prospect.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Full name of the lead (required)
        email: Email address (optional)
        phone: Phone number (optional)
        lead_source: Source of the lead e.g. website, referral, walk_in (optional)
        score: Lead score - hot, warm, or cold (optional, defaults to warm)
        notes: Additional notes (optional)
        deal_value: Expected deal value (optional)
    """
    client = get_api_client()
    try:
        data = {"name": name, "pipelineStage": "new"}

        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        if lead_source:
            data["leadSource"] = lead_source
        if score and score in ("hot", "warm", "cold"):
            data["score"] = score
        if notes:
            data["notes"] = notes
        if deal_value is not None:
            data["dealValue"] = deal_value

        response = await client.post("/leads", data)

        return {
            "success": True,
            "message": f"Lead '{name}' created successfully",
            "lead": {
                "id": response.get("id"),
                "name": response.get("name"),
                "stage": response.get("pipelineStage"),
                "score": response.get("score"),
            },
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def update_lead(
    lead_id: int,
    name: str = None,
    email: str = None,
    phone: str = None,
    score: str = None,
    notes: str = None,
    deal_value: float = None,
) -> dict:
    """Update a lead's details.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        lead_id: The ID of the lead to update (required)
        name: New name (optional)
        email: New email (optional)
        phone: New phone (optional)
        score: New score - hot, warm, or cold (optional)
        notes: New notes (optional)
        deal_value: New deal value (optional)
    """
    client = get_api_client()
    try:
        data = {}
        if name is not None:
            data["name"] = name
        if email is not None:
            data["email"] = email
        if phone is not None:
            data["phone"] = phone
        if score and score in ("hot", "warm", "cold"):
            data["score"] = score
        if notes is not None:
            data["notes"] = notes
        if deal_value is not None:
            data["dealValue"] = deal_value

        if not data:
            return {"error": "No fields to update", "success": False}

        response = await client.patch(f"/leads/{lead_id}", data)
        return {"success": True, "message": f"Lead {lead_id} updated", "lead": response}
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def update_lead_stage(lead_id: int, stage: str) -> dict:
    """Move a lead to a different pipeline stage.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        lead_id: The ID of the lead (required)
        stage: New pipeline stage. Valid values: new, contacted, tour_scheduled, tour_completed, proposal_sent, negotiation, won, lost
    """
    valid_stages = ["new", "contacted", "tour_scheduled", "tour_completed", "proposal_sent", "negotiation", "won", "lost"]
    if stage not in valid_stages:
        return {"error": f"Invalid stage. Must be one of: {', '.join(valid_stages)}", "success": False}

    client = get_api_client()
    try:
        response = await client.patch(f"/leads/{lead_id}/stage", {"stage": stage})
        return {
            "success": True,
            "message": f"Lead moved to '{stage}' stage",
            "lead": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def convert_lead_to_client(lead_id: int) -> dict:
    """Convert a won lead into a client/member account.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        lead_id: The ID of the lead to convert (required)
    """
    client = get_api_client()
    try:
        response = await client.patch(f"/leads/{lead_id}/convert", {})
        return {
            "success": True,
            "message": "Lead converted to client successfully",
            "lead": response.get("lead"),
            "user": response.get("user"),
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def get_lead_activities(lead_id: int) -> dict:
    """Get the activity/interaction history for a lead.

    Args:
        lead_id: The ID of the lead

    Use this tool when user asks about lead interactions, activity history, or follow-ups.
    """
    client = get_api_client()
    try:
        response = await client.get(f"/leads/{lead_id}/activities")
        activities = extract_list(response)
        return {"count": len(activities), "activities": activities}
    except Exception as e:
        return {"error": str(e)}


@tool
async def add_lead_activity(
    lead_id: int,
    activity_type: str,
    notes: str = None,
    scheduled_at: str = None,
) -> dict:
    """Log a new activity/interaction for a lead.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        lead_id: The ID of the lead (required)
        activity_type: Type of activity - call, email, tour, follow_up, note, meeting, sms (required)
        notes: Activity notes/details (optional)
        scheduled_at: Scheduled date/time in ISO format (optional)
    """
    valid_types = ["call", "email", "tour", "follow_up", "note", "meeting", "sms"]
    if activity_type not in valid_types:
        return {"error": f"Invalid type. Must be one of: {', '.join(valid_types)}", "success": False}

    client = get_api_client()
    try:
        data = {"type": activity_type}
        if notes:
            data["notes"] = notes
        if scheduled_at:
            data["scheduledAt"] = scheduled_at

        response = await client.post(f"/leads/{lead_id}/activities", data)
        return {"success": True, "message": "Activity logged", "activity": response}
    except Exception as e:
        return {"error": str(e), "success": False}
