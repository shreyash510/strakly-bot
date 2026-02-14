from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_engagement_dashboard() -> dict:
    """Get engagement scoring dashboard with risk distribution and overall stats.

    Use this tool when user asks about:
    - Engagement overview
    - Member engagement stats
    - Churn risk overview
    - Risk distribution
    - How engaged are members
    """
    client = get_api_client()
    try:
        response = await client.get("/engagement/dashboard")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_engagement_scores(risk_level: str = None) -> dict:
    """Get member engagement scores with optional risk level filter.

    Args:
        risk_level: Filter by risk level - low, medium, high, critical (optional)

    Use this tool when user asks about:
    - Engagement scores
    - At-risk members
    - Members with low engagement
    - High risk members
    - Who is likely to churn
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if risk_level and risk_level in ("low", "medium", "high", "critical"):
            params["riskLevel"] = risk_level

        response = await client.get("/engagement/scores", params)
        scores = extract_list(response)

        if not scores:
            return {"count": 0, "scores": [], "message": "No engagement scores found."}

        return {
            "count": len(scores),
            "scores": [
                {
                    "userId": s.get("userId"),
                    "userName": s.get("userName"),
                    "score": s.get("score"),
                    "riskLevel": s.get("riskLevel"),
                    "lastVisit": s.get("lastVisit"),
                    "visitFrequency": s.get("visitFrequency"),
                }
                for s in scores
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_churn_alerts(status: str = None) -> dict:
    """Get churn prediction alerts for at-risk members.

    Args:
        status: Filter by alert status - active, acknowledged (optional)

    Use this tool when user asks about:
    - Churn alerts
    - At-risk alerts
    - Members about to leave
    - Churn predictions
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if status:
            params["status"] = status

        response = await client.get("/engagement/alerts", params)
        alerts = extract_list(response)

        if not alerts:
            return {"count": 0, "alerts": [], "message": "No churn alerts found."}

        return {
            "count": len(alerts),
            "alerts": [
                {
                    "id": a.get("id"),
                    "userId": a.get("userId"),
                    "userName": a.get("userName"),
                    "alertType": a.get("alertType"),
                    "riskLevel": a.get("riskLevel"),
                    "message": a.get("message"),
                    "status": a.get("status"),
                    "createdAt": a.get("createdAt"),
                }
                for a in alerts
            ],
        }
    except Exception as e:
        return {"error": str(e)}
