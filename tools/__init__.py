from .base import APIClient, set_api_client, get_api_client
from .clients import get_clients_stats, get_clients_list, get_client_details, get_client_by_id, get_expiring_memberships, create_client, bulk_create_clients, update_client, bulk_update_clients, delete_client, bulk_delete_clients
from .memberships import get_client_membership, get_membership_stats, get_active_membership_clients
from .attendance import get_attendance_today, get_attendance_stats
from .revenue import get_revenue_stats, get_membership_sales
from .trainers import get_trainers_list, get_trainers_stats
from .enquiries import get_enquiries_list, get_enquiries_stats, create_enquiry, bulk_create_enquiries
from .gym import get_gym_info, get_branches_info, get_current_branch, create_branch
from .staff import get_managers_list, get_staff_list, get_staff_details, get_branch_admins_list, create_staff
from .salary import get_salary_by_name, get_staff_salary, get_salary_stats, get_pending_salaries, get_all_salaries
from .facilities import get_amenities_list, get_facilities_list, create_amenity, create_facility
from .diets import get_diet_plans, get_diet_by_id, get_client_diet, create_diet
from .plans import get_membership_plans, get_featured_plans, get_plan_details, create_plan
from .offers import get_offers_list, get_active_offers, get_offer_details, validate_offer_code, create_offer

__all__ = [
    "APIClient",
    "set_api_client",
    "get_api_client",
    # Clients
    "get_clients_stats",
    "get_clients_list",
    "get_client_details",
    "get_client_by_id",
    "get_expiring_memberships",
    "create_client",
    "bulk_create_clients",
    "update_client",
    "bulk_update_clients",
    "delete_client",
    "bulk_delete_clients",
    # Memberships
    "get_client_membership",
    "get_membership_stats",
    "get_active_membership_clients",
    # Attendance
    "get_attendance_today",
    "get_attendance_stats",
    # Revenue
    "get_revenue_stats",
    "get_membership_sales",
    # Trainers
    "get_trainers_list",
    "get_trainers_stats",
    # Enquiries
    "get_enquiries_list",
    "get_enquiries_stats",
    "create_enquiry",
    "bulk_create_enquiries",
    # Gym & Branches
    "get_gym_info",
    "get_branches_info",
    "get_current_branch",
    "create_branch",
    # Staff
    "get_managers_list",
    "get_staff_list",
    "get_staff_details",
    "get_branch_admins_list",
    "create_staff",
    # Salary
    "get_salary_by_name",
    "get_staff_salary",
    "get_salary_stats",
    "get_pending_salaries",
    "get_all_salaries",
    # Facilities & Amenities
    "get_amenities_list",
    "get_facilities_list",
    "create_amenity",
    "create_facility",
    # Diets
    "get_diet_plans",
    "get_diet_by_id",
    "get_client_diet",
    "create_diet",
    # Plans
    "get_membership_plans",
    "get_featured_plans",
    "get_plan_details",
    "create_plan",
    # Offers
    "get_offers_list",
    "get_active_offers",
    "get_offer_details",
    "validate_offer_code",
    "create_offer",
]
