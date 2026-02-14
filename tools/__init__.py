from .base import APIClient, set_api_client, get_api_client, cleanup_api_client, generate_password, extract_list
from .clients import (
    get_clients_stats, get_dashboard_overview, get_clients_list,
    get_client_details, get_client_by_id, get_expiring_memberships,
    create_client, bulk_create_clients, update_client,
    bulk_update_clients, delete_client, bulk_delete_clients,
)
from .memberships import (
    get_client_membership, get_membership_stats, get_active_membership_clients,
    freeze_membership, unfreeze_membership, get_freeze_history,
)
from .attendance import (
    get_attendance_today, get_attendance_stats, get_attendance_reports,
    get_attendance_by_date, get_all_attendance, get_present_count,
)
from .revenue import get_revenue_stats, get_membership_sales
from .trainers import get_trainers_list, get_trainers_stats
from .enquiries import get_enquiries_list, get_enquiries_stats, create_enquiry, bulk_create_enquiries
from .gym import get_gym_info, get_branches_info, get_current_branch, create_branch
from .staff import get_managers_list, get_staff_list, get_staff_details, get_branch_admins_list, create_staff
from .salary import get_salary_by_name, get_staff_salary, get_salary_stats, get_pending_salaries, get_all_salaries, create_salary
from .facilities import get_amenities_list, get_facilities_list, create_amenity, create_facility
from .diets import get_diet_plans, get_diet_by_id, get_client_diet, create_diet
from .plans import get_membership_plans, get_featured_plans, get_plan_details, create_plan
from .offers import get_offers_list, get_active_offers, get_offer_details, validate_offer_code, create_offer
from .theme import change_theme
from .navigate import navigate_to_page
from .leads import (
    get_leads_list, get_leads_stats, get_lead_details, create_lead,
    update_lead, update_lead_stage, convert_lead_to_client,
    get_lead_activities, add_lead_activity, get_lead_stage_history,
)
from .referrals import (
    get_referrals_list, get_referral_stats, get_user_referrals,
    create_referral, mark_referral_rewarded,
)
from .documents import (
    get_document_templates, get_template_details,
    get_signed_documents_for_user, create_document_template,
    get_signed_document_pdf,
)
from .goals import (
    get_member_goals, create_member_goal,
    update_goal_progress, update_goal_status,
    get_goal_milestones, create_goal_milestone, toggle_milestone_complete,
)
from .photos import get_member_photos, get_photo_details
from .notes import get_member_notes, create_member_note, toggle_note_pin
from .classes import get_class_types, get_class_sessions, get_session_bookings, get_my_class_bookings
from .appointments import get_services, get_trainer_availability, get_available_slots, get_appointments
from .guests import get_guest_visits, get_guest_visit_stats
from .products import get_products, get_low_stock_products, get_sales_stats
from .campaigns import get_campaigns, get_campaign_details
from .equipment import get_equipment, get_equipment_stats, get_upcoming_maintenance
from .custom_fields import get_custom_fields, get_entity_custom_values
from .engagement import get_engagement_dashboard, get_engagement_scores, get_churn_alerts
from .gamification import get_challenges, get_challenge_leaderboard, get_user_achievements, get_gamification_stats
from .loyalty import get_loyalty_dashboard, get_loyalty_tiers, get_user_loyalty_points, get_available_rewards
from .wearables import get_wearable_connections, get_wearable_summary, get_user_wearable_data
from .surveys import get_surveys, get_survey_analytics, get_latest_nps
from .currencies import get_currencies, convert_currency

# Single source of truth for all LangChain tools
ALL_TOOLS = [
    # Clients
    get_clients_stats, get_dashboard_overview, get_clients_list,
    get_client_details, get_client_by_id, get_expiring_memberships,
    create_client, bulk_create_clients, update_client,
    bulk_update_clients, delete_client, bulk_delete_clients,
    # Memberships
    get_client_membership, get_membership_stats, get_active_membership_clients,
    freeze_membership, unfreeze_membership, get_freeze_history,
    # Attendance
    get_attendance_today, get_attendance_stats, get_attendance_reports,
    get_attendance_by_date, get_all_attendance, get_present_count,
    # Revenue
    get_revenue_stats, get_membership_sales,
    # Trainers
    get_trainers_list, get_trainers_stats,
    # Enquiries
    get_enquiries_list, get_enquiries_stats, create_enquiry, bulk_create_enquiries,
    # Gym & Branches
    get_gym_info, get_branches_info, get_current_branch, create_branch,
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
    # Member Goals
    get_member_goals, create_member_goal,
    update_goal_progress, update_goal_status,
    get_goal_milestones, create_goal_milestone, toggle_milestone_complete,
    # Progress Photos
    get_member_photos, get_photo_details,
    # Member Notes
    get_member_notes, create_member_note, toggle_note_pin,
    # Classes (Group Scheduling)
    get_class_types, get_class_sessions, get_session_bookings, get_my_class_bookings,
    # Appointments (PT Booking)
    get_services, get_trainer_availability, get_available_slots, get_appointments,
    # Guest Visits
    get_guest_visits, get_guest_visit_stats,
    # Products (POS / Retail)
    get_products, get_low_stock_products, get_sales_stats,
    # Campaigns (Email / SMS)
    get_campaigns, get_campaign_details,
    # Equipment
    get_equipment, get_equipment_stats, get_upcoming_maintenance,
    # Custom Fields
    get_custom_fields, get_entity_custom_values,
    # Engagement Scoring & Churn
    get_engagement_dashboard, get_engagement_scores, get_churn_alerts,
    # Gamification
    get_challenges, get_challenge_leaderboard, get_user_achievements, get_gamification_stats,
    # Loyalty / Rewards
    get_loyalty_dashboard, get_loyalty_tiers, get_user_loyalty_points, get_available_rewards,
    # Wearables
    get_wearable_connections, get_wearable_summary, get_user_wearable_data,
    # Surveys & NPS
    get_surveys, get_survey_analytics, get_latest_nps,
    # Currencies
    get_currencies, convert_currency,
]

# Tool name → function lookup
TOOL_MAP = {t.name: t for t in ALL_TOOLS}
