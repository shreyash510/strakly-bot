from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_services() -> dict:
    """Get all available PT/appointment services.

    Use this tool when user asks about:
    - Available services
    - PT session types
    - What services are offered
    - Personal training options
    """
    client = get_api_client()
    try:
        response = await client.get("/appointments/services", {"limit": 100})
        services = extract_list(response)

        if not services:
            return {"count": 0, "services": [], "message": "No services found."}

        return {
            "count": len(services),
            "services": [
                {
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "description": s.get("description"),
                    "durationMinutes": s.get("durationMinutes"),
                    "price": s.get("price"),
                    "maxParticipants": s.get("maxParticipants"),
                    "category": s.get("category"),
                }
                for s in services
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_trainer_availability(trainer_id: int) -> dict:
    """Get a trainer's weekly availability schedule.

    Args:
        trainer_id: The trainer's user ID (required)

    Use this tool when user asks about:
    - When is a trainer available
    - Trainer's schedule
    - Available time slots for a trainer
    """
    client = get_api_client()
    try:
        response = await client.get(f"/appointments/availability/{trainer_id}")
        slots = extract_list(response)

        if not slots:
            return {"count": 0, "availability": [], "message": "No availability set for this trainer."}

        return {
            "count": len(slots),
            "availability": [
                {
                    "dayOfWeek": s.get("dayOfWeek"),
                    "startTime": s.get("startTime"),
                    "endTime": s.get("endTime"),
                    "isAvailable": s.get("isAvailable"),
                }
                for s in slots
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_available_slots(trainer_id: int, date: str) -> dict:
    """Get available appointment time slots for a trainer on a specific date.

    Args:
        trainer_id: The trainer's user ID (required)
        date: The date in YYYY-MM-DD format (required)

    Use this tool when user asks about:
    - Available slots for booking
    - Open times for a trainer on a date
    - When can I book with trainer
    """
    client = get_api_client()
    try:
        response = await client.get("/appointments/available-slots", {
            "trainerId": trainer_id,
            "date": date,
        })
        slots = extract_list(response)

        if not slots:
            return {"count": 0, "slots": [], "message": f"No available slots for this trainer on {date}."}

        return {
            "count": len(slots),
            "slots": slots,
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_appointments(status: str = None) -> dict:
    """Get appointments list with optional status filter.

    Args:
        status: Filter by status - booked, confirmed, completed, cancelled, no_show (optional)

    Use this tool when user asks about:
    - Upcoming appointments
    - Appointment list
    - Booked sessions
    - Cancelled appointments
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if status and status in ("booked", "confirmed", "completed", "cancelled", "no_show"):
            params["status"] = status

        response = await client.get("/appointments", params)
        appointments = extract_list(response)

        if not appointments:
            return {"count": 0, "appointments": [], "message": "No appointments found."}

        return {
            "count": len(appointments),
            "appointments": [
                {
                    "id": a.get("id"),
                    "serviceName": a.get("serviceName"),
                    "trainerName": a.get("trainerName"),
                    "clientName": a.get("clientName") or a.get("userName"),
                    "startTime": a.get("startTime"),
                    "endTime": a.get("endTime"),
                    "status": a.get("status"),
                }
                for a in appointments
            ],
        }
    except Exception as e:
        return {"error": str(e)}
