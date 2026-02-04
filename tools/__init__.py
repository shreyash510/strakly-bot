from .base import APIClient, set_api_client, get_api_client
from .clients import get_clients_stats, get_clients_list, get_client_details, get_client_by_id, get_expiring_memberships
from .memberships import get_client_membership, get_membership_stats, get_active_membership_clients
from .attendance import get_attendance_today, get_attendance_stats
from .revenue import get_revenue_stats, get_membership_sales
from .trainers import get_trainers_list, get_trainers_stats
from .enquiries import get_enquiries_list, get_enquiries_stats
from .gym import get_gym_info, get_branches_info, get_current_branch
from .staff import get_managers_list, get_staff_list, get_staff_details, get_branch_admins_list
from .salary import get_staff_salary, get_salary_stats, get_pending_salaries, get_all_salaries

__all__ = [
    "APIClient",
    "set_api_client",
    "get_api_client",
    "get_clients_stats",
    "get_clients_list",
    "get_client_details",
    "get_client_by_id",
    "get_expiring_memberships",
    "get_client_membership",
    "get_membership_stats",
    "get_active_membership_clients",
    "get_attendance_today",
    "get_attendance_stats",
    "get_revenue_stats",
    "get_membership_sales",
    "get_trainers_list",
    "get_trainers_stats",
    "get_enquiries_list",
    "get_enquiries_stats",
    "get_gym_info",
    "get_branches_info",
    "get_current_branch",
    "get_managers_list",
    "get_staff_list",
    "get_staff_details",
    "get_branch_admins_list",
    "get_staff_salary",
    "get_salary_stats",
    "get_pending_salaries",
    "get_all_salaries",
]
