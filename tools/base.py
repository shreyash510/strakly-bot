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

    async def get(self, endpoint: str, params: dict = None) -> dict:
        """Make GET request to backend API"""
        # Include branch_id in params if set
        if params is None:
            params = {}
        if self.branch_id is not None:
            params["branchId"] = self.branch_id

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def post(self, endpoint: str, data: dict = None) -> dict:
        """Make POST request to backend API"""
        # Include branch_id in data if set
        if data is None:
            data = {}
        if self.branch_id is not None:
            data["branchId"] = self.branch_id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()


# Global client instance (set per request)
_current_client: APIClient | None = None


def set_api_client(token: str, branch_id: int = None):
    """Set the API client for current request context"""
    global _current_client
    _current_client = APIClient(token, branch_id)


def get_api_client() -> APIClient:
    """Get the current API client"""
    if _current_client is None:
        raise RuntimeError("API client not initialized. Call set_api_client first.")
    return _current_client


def get_current_branch_id() -> int | None:
    """Get the current branch ID from the API client"""
    if _current_client is None:
        return None
    return _current_client.branch_id
