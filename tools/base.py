import contextvars
import secrets
import string
import httpx
from config import config


class APIClient:
    """HTTP client for calling NestJS backend APIs"""

    def __init__(self, token: str, branch_id: int = None):
        self.base_url = config.BACKEND_API_URL
        self.token = token
        self.branch_id = branch_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0,
        )

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response — raise on error, parse JSON on success."""
        if response.status_code >= 400:
            try:
                error_body = response.json()
                error_msg = error_body.get("message", response.text)
                if isinstance(error_msg, list):
                    error_msg = "; ".join(error_msg)
                raise httpx.HTTPStatusError(
                    f"{response.status_code}: {error_msg}",
                    request=response.request,
                    response=response,
                )
            except (ValueError, KeyError):
                response.raise_for_status()
        if response.status_code == 204 or not response.text:
            return {"success": True}
        return response.json()

    def _inject_branch(self, params: dict) -> dict:
        """Inject branch_id into params/data if set."""
        if self.branch_id is not None:
            params["branchId"] = self.branch_id
        return params

    async def get(self, endpoint: str, params: dict = None) -> dict:
        """Make GET request to backend API"""
        params = self._inject_branch(params or {})
        response = await self._http.get(endpoint, params=params)
        return self._handle_response(response)

    async def post(self, endpoint: str, data: dict = None) -> dict:
        """Make POST request to backend API"""
        data = self._inject_branch(data or {})
        response = await self._http.post(endpoint, json=data)
        return self._handle_response(response)

    async def patch(self, endpoint: str, data: dict = None) -> dict:
        """Make PATCH request to backend API"""
        data = self._inject_branch(data or {})
        response = await self._http.patch(endpoint, json=data)
        return self._handle_response(response)

    async def delete(self, endpoint: str, data: dict = None) -> dict:
        """Make DELETE request to backend API"""
        data = self._inject_branch(data or {})
        response = await self._http.request("DELETE", endpoint, json=data)
        return self._handle_response(response)

    async def aclose(self):
        """Close the underlying HTTP client."""
        await self._http.aclose()


# Request-scoped API client using contextvars (safe for concurrent async requests)
_current_client: contextvars.ContextVar[APIClient | None] = contextvars.ContextVar(
    "_current_client", default=None
)


async def cleanup_api_client():
    """Close the current API client's HTTP connection."""
    client = _current_client.get()
    if client:
        await client.aclose()
        _current_client.set(None)


def set_api_client(token: str, branch_id: int = None):
    """Set the API client for current request context."""
    _current_client.set(APIClient(token, branch_id))


def get_api_client() -> APIClient:
    """Get the current API client"""
    client = _current_client.get()
    if client is None:
        raise RuntimeError("API client not initialized. Call set_api_client first.")
    return client


def get_current_branch_id() -> int | None:
    """Get the current branch ID from the API client"""
    client = _current_client.get()
    if client is None:
        return None
    return client.branch_id


def generate_password(length: int = 12) -> str:
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def extract_list(response: dict | list, key: str = "data") -> list:
    """Extract list from API response, handling both {data: [...]} and [...] formats."""
    data = response.get(key, response) if isinstance(response, dict) else response
    return data if isinstance(data, list) else []


def extract_paginated(response: dict | list, key: str = "data") -> tuple[list, dict]:
    """Extract list + pagination metadata from API response.
    Returns (items, pagination_dict).
    """
    if isinstance(response, dict):
        data = response.get(key, [])
        if not isinstance(data, list):
            data = []
        pagination = response.get("pagination", {})
        return data, pagination
    return (response if isinstance(response, list) else []), {}
