import jwt
from fastapi import HTTPException, status
from config import config


class TenantContext:
    """Holds tenant-specific context extracted from JWT"""

    def __init__(
        self,
        user_id: int,
        gym_id: int,
        branch_id: int | None,
        role: str,
        email: str,
        name: str,
    ):
        self.user_id = user_id
        self.gym_id = gym_id
        self.branch_id = branch_id
        self.role = role
        self.email = email
        self.name = name

    def __repr__(self):
        return f"TenantContext(user_id={self.user_id}, gym_id={self.gym_id}, branch_id={self.branch_id}, role={self.role})"


def decode_token(token: str) -> TenantContext:
    """Decode JWT token and extract tenant context"""
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM],
        )

        return TenantContext(
            user_id=payload.get("sub") or payload.get("userId"),
            gym_id=payload.get("gymId"),
            branch_id=payload.get("branchId"),
            role=payload.get("role", "client"),
            email=payload.get("email", ""),
            name=payload.get("name", ""),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
