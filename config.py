import os
import sys
from dotenv import load_dotenv

load_dotenv()


class Config:
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Backend API
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:3000/api")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # CORS
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3001",
        ).split(",")
        if o.strip()
    ]

    # Public bot rate limiting
    PUBLIC_RATE_LIMIT: int = int(os.getenv("PUBLIC_RATE_LIMIT", "30"))
    PUBLIC_RATE_WINDOW: int = int(os.getenv("PUBLIC_RATE_WINDOW", "600"))

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: int = int(os.getenv("BOT_PORT", "8001"))

    def validate(self):
        """Validate required secrets are set. Call at startup."""
        missing = []
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not self.JWT_SECRET:
            missing.append("JWT_SECRET")
        if missing:
            print(f"FATAL: Missing required env vars: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)


config = Config()
config.validate()
