from langchain_core.tools import tool


@tool
async def navigate_to_page(path: str) -> dict:
    """Navigate the user to a specific page in the app.

    Use this when user says "go to", "open", "take me to", "show me [page]".

    Args:
        path: The route path, e.g. "/dashboard", "/clients", "/clients/5?tab=attendance"

    Common pages:
    - /dashboard
    - /clients, /clients/:id
    - /trainers, /trainers/:id
    - /managers, /managers/:id
    - /branch-admins, /branch-admins/:id
    - /branches, /branches/:id
    - /attendance
    - /memberships
    - /membership-plan (subscription overview)
    - /membership-plan/member/:id (subscription details)
    - /plans, /offers
    - /salary
    - /diet, /diet/:id
    - /facilities, /amenities
    - /financial-reports
    - /announcements, /announcements/:id
    - /settings, /profile
    - /gym-profile, /gym-subscription
    - /gym, /gym/:id (superadmin)
    - /users, /users/:id (superadmin)
    - /support, /support/:id
    - /share-app
    - /health-fitness
    - /my-subscription, /my-attendance, /my-trainer, /my-salary
    - /data-migration

    Tab navigation (append ?tab=<tab_name> to the path):

    Client detail /clients/:id tabs:
      information, attendance, trainer, body-metrics, subscription, diet, permissions

    Trainer detail /trainers/:id tabs:
      information, clients

    Manager detail /managers/:id tabs:
      information, permissions

    Gym detail /gym/:id tabs:
      information, owner, subscription, branches

    User detail /users/:id tabs:
      information, gym

    Subscription detail /membership-plan/member/:id tabs:
      membership, payments

    Salary page /salary tabs:
      overview, salary

    Memberships page /memberships tabs:
      overview, clients

    Subscription page /membership-plan tabs:
      overview, clients, plans, offers

    Health & Fitness page /health-fitness tabs:
      information, insights, history
    """
    if not path or not path.startswith("/"):
        return {"success": False, "error": "Path must start with /"}

    return {"success": True, "actions": [{"type": "navigate", "value": path}]}
