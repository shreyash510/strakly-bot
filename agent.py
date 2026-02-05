from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from config import config
from prompts import SYSTEM_PROMPT
from tools import (
    set_api_client,
    # Clients
    get_clients_stats,
    get_clients_list,
    get_client_details,
    get_client_by_id,
    get_expiring_memberships,
    create_client,
    bulk_create_clients,
    update_client,
    bulk_update_clients,
    delete_client,
    bulk_delete_clients,
    # Memberships
    get_client_membership,
    get_membership_stats,
    get_active_membership_clients,
    # Attendance
    get_attendance_today,
    get_attendance_stats,
    # Revenue
    get_revenue_stats,
    get_membership_sales,
    # Trainers
    get_trainers_list,
    get_trainers_stats,
    # Enquiries
    get_enquiries_list,
    get_enquiries_stats,
    create_enquiry,
    bulk_create_enquiries,
    # Gym & Branches
    get_gym_info,
    get_branches_info,
    get_current_branch,
    create_branch,
    # Staff
    get_managers_list,
    get_staff_list,
    get_staff_details,
    get_branch_admins_list,
    create_staff,
    # Salary
    get_salary_by_name,
    get_staff_salary,
    get_salary_stats,
    get_pending_salaries,
    get_all_salaries,
    # Facilities & Amenities
    get_amenities_list,
    get_facilities_list,
    create_amenity,
    create_facility,
    # Diets
    get_diet_plans,
    get_diet_by_id,
    get_client_diet,
    create_diet,
    # Plans
    get_membership_plans,
    get_featured_plans,
    get_plan_details,
    create_plan,
    # Offers
    get_offers_list,
    get_active_offers,
    get_offer_details,
    validate_offer_code,
    create_offer,
)
from auth import TenantContext
import uuid

# All available tools
ALL_TOOLS = [
    # Clients
    get_clients_stats,
    get_clients_list,
    get_client_details,
    get_client_by_id,
    get_expiring_memberships,
    create_client,
    bulk_create_clients,
    update_client,
    bulk_update_clients,
    delete_client,
    bulk_delete_clients,
    # Memberships
    get_client_membership,
    get_membership_stats,
    get_active_membership_clients,
    # Attendance
    get_attendance_today,
    get_attendance_stats,
    # Revenue
    get_revenue_stats,
    get_membership_sales,
    # Trainers
    get_trainers_list,
    get_trainers_stats,
    # Enquiries
    get_enquiries_list,
    get_enquiries_stats,
    create_enquiry,
    bulk_create_enquiries,
    # Gym & Branches
    get_gym_info,
    get_branches_info,
    get_current_branch,
    create_branch,
    # Staff
    get_managers_list,
    get_staff_list,
    get_staff_details,
    get_branch_admins_list,
    create_staff,
    # Salary
    get_salary_by_name,
    get_staff_salary,
    get_salary_stats,
    get_pending_salaries,
    get_all_salaries,
    # Facilities & Amenities
    get_amenities_list,
    get_facilities_list,
    create_amenity,
    create_facility,
    # Diets
    get_diet_plans,
    get_diet_by_id,
    get_client_diet,
    create_diet,
    # Plans
    get_membership_plans,
    get_featured_plans,
    get_plan_details,
    create_plan,
    # Offers
    get_offers_list,
    get_active_offers,
    get_offer_details,
    validate_offer_code,
    create_offer,
]

# Tool name to function mapping
TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

# In-memory conversation store (temporary per session)
conversations: dict[str, list] = {}


def get_llm_with_tools():
    """Create LLM instance with tools bound"""
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        temperature=0,
        api_key=config.OPENAI_API_KEY,
    )
    return llm.bind_tools(ALL_TOOLS)


async def process_chat(
    message: str,
    token: str,
    tenant: TenantContext,
    conversation_id: str = None,
    branch_id: int = None,
) -> dict:
    """Process a chat message and return response"""

    # Set API client with user's token and branch
    set_api_client(token, branch_id)

    # Get or create conversation
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in conversations:
        conversations[conversation_id] = []

    conversation = conversations[conversation_id]

    # Build messages
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add conversation history (last 20 messages for context)
    for msg in conversation[-20:]:
        messages.append(msg)

    # Add current user message
    user_message = HumanMessage(content=message)
    messages.append(user_message)
    conversation.append(user_message)

    # Get LLM with tools
    llm = get_llm_with_tools()

    # Track tools used
    tools_used = []

    # Agent loop - process until no more tool calls
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Get LLM response
        response = await llm.ainvoke(messages)
        messages.append(response)

        # Store AI response in conversation history (preserves tool_calls context)
        conversation.append(response)

        # If no tool calls, we're done
        if not response.tool_calls:
            break

        # Process tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            tools_used.append(tool_name)

            # Get and execute tool
            if tool_name in TOOL_MAP:
                try:
                    tool_fn = TOOL_MAP[tool_name]
                    result = await tool_fn.ainvoke(tool_args)
                    tool_result = str(result)
                except Exception as e:
                    tool_result = f"Error executing tool: {str(e)}"
            else:
                tool_result = f"Unknown tool: {tool_name}"

            # Add tool result to messages and conversation history
            tool_message = ToolMessage(
                content=tool_result,
                tool_call_id=tool_call["id"],
            )
            messages.append(tool_message)
            conversation.append(tool_message)

    # Get final response text
    final_response = response.content if response.content else "I couldn't process that request. Please try again."

    # Limit conversation history size
    if len(conversations[conversation_id]) > 40:
        conversations[conversation_id] = conversations[conversation_id][-40:]

    return {
        "success": True,
        "response": final_response,
        "conversation_id": conversation_id,
        "tools_used": list(set(tools_used)),
    }


def clear_conversation(conversation_id: str):
    """Clear a conversation from memory"""
    if conversation_id in conversations:
        del conversations[conversation_id]
