from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_surveys(status: str = None) -> dict:
    """Get surveys list with optional status filter.

    Args:
        status: Filter by status - draft, active, closed (optional)

    Use this tool when user asks about:
    - Surveys list
    - Active surveys
    - NPS surveys
    - Feedback forms
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if status:
            params["status"] = status

        response = await client.get("/surveys", params)
        surveys = extract_list(response)

        if not surveys:
            return {"count": 0, "surveys": [], "message": "No surveys found."}

        return {
            "count": len(surveys),
            "surveys": [
                {
                    "id": s.get("id"),
                    "title": s.get("title"),
                    "type": s.get("type"),
                    "status": s.get("status"),
                    "responseCount": s.get("responseCount"),
                    "createdAt": s.get("createdAt"),
                }
                for s in surveys
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_survey_analytics(survey_id: int) -> dict:
    """Get analytics and NPS score for a specific survey.

    Args:
        survey_id: The survey ID (required)

    Use this tool when user asks about:
    - Survey results
    - Survey analytics
    - NPS score for a survey
    - Survey response breakdown
    """
    client = get_api_client()
    try:
        response = await client.get(f"/surveys/{survey_id}/analytics")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_latest_nps() -> dict:
    """Get the latest Net Promoter Score (NPS) for the gym.

    Use this tool when user asks about:
    - NPS score
    - Net Promoter Score
    - Customer satisfaction score
    - Latest NPS
    """
    client = get_api_client()
    try:
        response = await client.get("/surveys/nps/latest")
        return response
    except Exception as e:
        return {"error": str(e)}
