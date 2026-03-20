"""Dynamic tool selection to stay within the 128-tool limit.

Categorises the 138 LangChain tools, matches user messages against
keyword rules, and returns only the relevant subset (always ≤ 128).
Zero latency cost — pure keyword matching, no extra LLM call.
"""

import logging
from langchain_core.messages import HumanMessage

from tools import (
    # Clients
    get_clients_stats, get_dashboard_overview, get_clients_list,
    get_client_details, get_client_by_id, get_expiring_memberships,
    create_client, bulk_create_clients, update_client,
    bulk_update_clients, delete_client, bulk_delete_clients,
    # Memberships
    get_client_membership, get_membership_stats, get_active_membership_clients,
    freeze_membership, unfreeze_membership, get_freeze_history,
    renew_membership,
    # Attendance
    get_attendance_today, get_attendance_stats, get_attendance_reports,
    get_attendance_by_date, get_all_attendance, get_present_count,
    # Revenue
    get_revenue_stats, get_membership_sales,
    # Trainers
    get_trainers_list, get_trainers_stats,
    # Enquiries
    get_enquiries_list, get_enquiries_stats, create_enquiry, bulk_create_enquiries,
    # Gym
    get_gym_info,
    # Staff
    get_managers_list, get_staff_list, get_staff_details, get_branch_admins_list, create_staff,
    # Salary
    get_salary_by_name, get_staff_salary, get_salary_stats, get_pending_salaries, get_all_salaries, create_salary,
    # Facilities & Amenities
    get_amenities_list, get_facilities_list, create_amenity, create_facility,
    # Diets
    get_diet_plans, get_diet_by_id, get_client_diet, create_diet,
    # Plans
    get_membership_plans, get_featured_plans, get_plan_details, create_plan,
    # Offers
    get_offers_list, get_active_offers, get_offer_details, validate_offer_code, create_offer,
    # Theme
    change_theme,
    # Navigation
    navigate_to_page,
    # Leads CRM
    get_leads_list, get_leads_stats, get_lead_details, create_lead,
    update_lead, update_lead_stage, convert_lead_to_client,
    get_lead_activities, add_lead_activity, get_lead_stage_history,
    # Referrals
    get_referrals_list, get_referral_stats, get_user_referrals,
    create_referral, mark_referral_rewarded,
    # Documents & Waivers
    get_document_templates, get_template_details,
    get_signed_documents_for_user, create_document_template,
    get_signed_document_pdf,
    # Client Goals
    get_client_goals, create_client_goal,
    update_goal_progress, update_goal_status,
    get_goal_milestones, create_goal_milestone, toggle_milestone_complete,
    # Progress Photos
    get_client_photos, get_photo_details,
    # Client Notes
    get_client_notes, create_client_note, toggle_note_pin,
    # Classes
    get_class_types, get_class_sessions, get_session_bookings, get_my_class_bookings,
    # Appointments
    get_services, get_trainer_availability, get_available_slots, get_appointments,
    # Guest Visits
    get_guest_visits, get_guest_visit_stats,
    # Products
    get_products, get_low_stock_products, get_sales_stats,
    void_product_sale, void_batch_sale, get_product_sales,
    # Campaigns
    get_campaigns, get_campaign_details,
    # Equipment
    get_equipment, get_equipment_stats, get_upcoming_maintenance,
    # Custom Fields
    get_custom_fields, get_entity_custom_values,
    # Engagement
    get_engagement_dashboard, get_engagement_scores, get_churn_alerts,
    # Gamification
    get_challenges, get_challenge_leaderboard, get_user_achievements, get_gamification_stats,
    # Loyalty
    get_loyalty_dashboard, get_loyalty_tiers, get_user_loyalty_points, get_available_rewards,
    # Wearables
    get_wearable_connections, get_wearable_summary, get_user_wearable_data,
    # Surveys
    get_surveys, get_survey_analytics, get_latest_nps,
    # Currencies
    get_currencies, convert_currency,
)

logger = logging.getLogger(__name__)

# ── Always-included tools (8) ──────────────────────────────────────
CORE_TOOLS = [
    change_theme, navigate_to_page,
    get_gym_info,
    get_currencies, convert_currency,
]

# ── Tool categories ────────────────────────────────────────────────
TOOL_CATEGORIES: dict[str, list] = {
    "clients": [
        get_clients_stats, get_dashboard_overview, get_clients_list,
        get_client_details, get_client_by_id, get_expiring_memberships,
        create_client, bulk_create_clients, update_client,
        bulk_update_clients, delete_client, bulk_delete_clients,
    ],
    "memberships": [
        get_client_membership, get_membership_stats, get_active_membership_clients,
        freeze_membership, unfreeze_membership, get_freeze_history,
        renew_membership,
    ],
    "attendance": [
        get_attendance_today, get_attendance_stats, get_attendance_reports,
        get_attendance_by_date, get_all_attendance, get_present_count,
    ],
    "revenue": [
        get_revenue_stats, get_membership_sales,
    ],
    "trainers": [
        get_trainers_list, get_trainers_stats,
    ],
    "enquiries": [
        get_enquiries_list, get_enquiries_stats, create_enquiry, bulk_create_enquiries,
    ],
    "staff": [
        get_managers_list, get_staff_list, get_staff_details, get_branch_admins_list, create_staff,
    ],
    "salary": [
        get_salary_by_name, get_staff_salary, get_salary_stats,
        get_pending_salaries, get_all_salaries, create_salary,
    ],
    "facilities": [
        get_amenities_list, get_facilities_list, create_amenity, create_facility,
    ],
    "diets": [
        get_diet_plans, get_diet_by_id, get_client_diet, create_diet,
    ],
    "plans": [
        get_membership_plans, get_featured_plans, get_plan_details, create_plan,
    ],
    "offers": [
        get_offers_list, get_active_offers, get_offer_details, validate_offer_code, create_offer,
    ],
    "leads": [
        get_leads_list, get_leads_stats, get_lead_details, create_lead,
        update_lead, update_lead_stage, convert_lead_to_client,
        get_lead_activities, add_lead_activity, get_lead_stage_history,
    ],
    "referrals": [
        get_referrals_list, get_referral_stats, get_user_referrals,
        create_referral, mark_referral_rewarded,
    ],
    "documents": [
        get_document_templates, get_template_details,
        get_signed_documents_for_user, create_document_template,
        get_signed_document_pdf,
    ],
    "goals": [
        get_client_goals, create_client_goal,
        update_goal_progress, update_goal_status,
        get_goal_milestones, create_goal_milestone, toggle_milestone_complete,
    ],
    "photos": [
        get_client_photos, get_photo_details,
    ],
    "notes": [
        get_client_notes, create_client_note, toggle_note_pin,
    ],
    "classes": [
        get_class_types, get_class_sessions, get_session_bookings, get_my_class_bookings,
    ],
    "appointments": [
        get_services, get_trainer_availability, get_available_slots, get_appointments,
    ],
    "guests": [
        get_guest_visits, get_guest_visit_stats,
    ],
    "products": [
        get_products, get_low_stock_products, get_sales_stats,
        void_product_sale, void_batch_sale, get_product_sales,
    ],
    "campaigns": [
        get_campaigns, get_campaign_details,
    ],
    "equipment": [
        get_equipment, get_equipment_stats, get_upcoming_maintenance,
    ],
    "custom_fields": [
        get_custom_fields, get_entity_custom_values,
    ],
    "engagement": [
        get_engagement_dashboard, get_engagement_scores, get_churn_alerts,
    ],
    "gamification": [
        get_challenges, get_challenge_leaderboard, get_user_achievements, get_gamification_stats,
    ],
    "loyalty": [
        get_loyalty_dashboard, get_loyalty_tiers, get_user_loyalty_points, get_available_rewards,
    ],
    "wearables": [
        get_wearable_connections, get_wearable_summary, get_user_wearable_data,
    ],
    "surveys": [
        get_surveys, get_survey_analytics, get_latest_nps,
    ],
}

# ── Keyword → category mapping ────────────────────────────────────
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "clients": [
        "client", "member", "customer", "person", "user", "people",
        "who", "profile", "add client", "create client", "delete client",
        "update client", "bulk", "expiring",
    ],
    "memberships": [
        "membership", "freeze", "unfreeze", "expire", "renew",
        "subscription", "active member", "suspended",
    ],
    "attendance": [
        "attendance", "check-in", "checkin", "check in", "present",
        "absent", "came today", "who came", "today",
    ],
    "revenue": [
        "revenue", "income", "money", "earning", "payment", "sales",
        "financial", "billing", "collection",
    ],
    "trainers": [
        "trainer", "coach", "instructor", "personal training", "pt",
    ],
    "enquiries": [
        "enquiry", "enquiries", "inquiry", "inquiries", "prospect",
        "interested", "new enquiry",
    ],
    "staff": [
        "staff", "manager", "employee", "receptionist", "team",
        "branch admin",
    ],
    "salary": [
        "salary", "pay", "wage", "payroll", "compensation",
        "pending salary", "salary stats",
    ],
    "facilities": [
        "facility", "amenity", "amenities", "pool", "sauna",
        "studio", "room", "locker",
    ],
    "diets": [
        "diet", "nutrition", "meal", "food", "calorie", "eating",
        "diet plan", "macro",
    ],
    "plans": [
        "plan", "package", "pricing", "tier", "price",
        "membership plan", "featured plan",
    ],
    "offers": [
        "offer", "discount", "promotion", "coupon", "deal", "code",
        "promo", "validate code",
    ],
    "leads": [
        "lead", "crm", "pipeline", "follow-up", "follow up",
        "stage", "convert lead", "lead activity",
    ],
    "referrals": [
        "referral", "refer", "referred", "invite", "referral reward",
    ],
    "documents": [
        "document", "waiver", "template", "sign", "contract", "pdf",
        "signed document",
    ],
    "goals": [
        "goal", "target", "milestone", "progress", "fitness goal",
        "client goal",
    ],
    "photos": [
        "photo", "picture", "image", "transformation",
        "progress photo", "before after",
    ],
    "notes": [
        "note", "comment", "remark", "memo", "pin note",
    ],
    "classes": [
        "class", "session", "group class", "yoga", "zumba", "pilates",
        "group session", "booking", "class type",
    ],
    "appointments": [
        "appointment", "slot", "availability", "book appointment",
        "schedule", "available slot", "service",
    ],
    "guests": [
        "guest", "visitor", "walk-in", "walk in", "day pass", "trial",
        "guest visit",
    ],
    "products": [
        "product", "inventory", "stock", "retail", "pos", "shop",
        "store", "sell", "low stock", "void", "batch", "sale",
    ],
    "campaigns": [
        "campaign", "email campaign", "sms", "marketing",
        "notification", "broadcast",
    ],
    "equipment": [
        "equipment", "machine", "maintenance", "treadmill", "weights",
        "repair", "servicing",
    ],
    "custom_fields": [
        "custom field", "extra field", "additional field",
        "custom value",
    ],
    "engagement": [
        "engagement", "churn", "at-risk", "at risk", "inactive",
        "engagement score",
    ],
    "gamification": [
        "challenge", "leaderboard", "badge", "achievement",
        "gamification", "compete",
    ],
    "loyalty": [
        "loyalty", "reward", "loyalty tier", "loyalty points",
        "redeem", "loyalty program",
    ],
    "wearables": [
        "wearable", "fitbit", "apple watch", "garmin", "device",
        "sync", "steps", "heart rate", "health data",
    ],
    "surveys": [
        "survey", "nps", "feedback", "questionnaire", "rating",
        "net promoter",
    ],
}

# ── Related categories (auto-include when one is matched) ──────────
RELATED_CATEGORIES: dict[str, list[str]] = {
    "clients": ["memberships", "attendance"],
    "salary": ["staff"],
    "trainers": ["staff"],
    "appointments": ["trainers", "clients"],
    "classes": ["clients"],
    "leads": ["clients", "enquiries"],
    "plans": ["offers"],
    "memberships": ["clients"],
    "goals": ["clients"],
    "photos": ["clients"],
    "notes": ["clients"],
    "documents": ["clients"],
}

# Categories to include when no keywords match (generic question)
DEFAULT_CATEGORIES = [
    "clients", "memberships", "attendance", "revenue",
    "plans", "trainers", "enquiries",
]

MAX_TOOLS = 128


def select_tools(message: str, conversation_history: list | None = None) -> list:
    """Pick the relevant tool subset for a user message.

    Scans the current message (and recent conversation context) for
    keyword matches, selects matching categories + their related ones,
    and returns a deduplicated list capped at 128 tools.
    """
    # Build search text from current message + recent human messages
    text = message.lower()
    if conversation_history:
        # Include last 4 human messages for multi-turn context
        recent_human = [
            msg.content.lower()
            for msg in conversation_history[-8:]
            if isinstance(msg, HumanMessage)
        ][-4:]
        text = text + " " + " ".join(recent_human)

    # Find matching categories
    matched: set[str] = set()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matched.add(category)
                break

    # Expand with related categories
    expanded: set[str] = set(matched)
    for cat in matched:
        for related in RELATED_CATEGORIES.get(cat, []):
            expanded.add(related)

    # If nothing matched, use broad defaults
    if not expanded:
        expanded = set(DEFAULT_CATEGORIES)

    # Collect tools: core + matched categories
    seen_ids: set[int] = set()
    selected: list = []

    def _add_tools(tools: list):
        for tool in tools:
            tid = id(tool)
            if tid not in seen_ids:
                seen_ids.add(tid)
                selected.append(tool)

    _add_tools(CORE_TOOLS)
    for cat in expanded:
        if cat in TOOL_CATEGORIES:
            _add_tools(TOOL_CATEGORIES[cat])

    # Safety cap — if somehow over 128, trim non-core categories
    if len(selected) > MAX_TOOLS:
        # Keep core, trim extras from the end
        core_count = len(CORE_TOOLS)
        selected = selected[:MAX_TOOLS]
        logger.warning(
            "Tool selection trimmed to %d (matched categories: %s)",
            len(selected), sorted(expanded),
        )

    logger.info(
        "Tool selection: %d/%d tools, categories=%s",
        len(selected), sum(len(v) for v in TOOL_CATEGORIES.values()) + len(CORE_TOOLS),
        sorted(expanded),
    )

    return selected
