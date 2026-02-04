import httpx
from config import config


class APIClient:
    """HTTP client for calling NestJS backend APIs"""

    def __init__(self, token: str):
        self.base_url = config.BACKEND_API_URL
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get(self, endpoint: str, params: dict = None) -> dict:
        """Make GET request to backend API"""
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


def set_api_client(token: str):
    """Set the API client for current request context"""
    global _current_client
    _current_client = APIClient(token)


def get_api_client() -> APIClient:
    """Get the current API client"""
    if _current_client is None:
        raise RuntimeError("API client not initialized. Call set_api_client first.")
    return _current_client
