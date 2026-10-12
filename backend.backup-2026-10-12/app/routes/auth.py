from hashlib import sha256

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

USERS = {"demo@placementpulse.com": {"name": "Demo Student", "password": "placementpulse", "role": "student"}}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def _token(email: str) -> str:
    return sha256(f"placementpulse:{email}".encode()).hexdigest()


@router.post("/auth/login")
def login(request: LoginRequest) -> dict:
    user = USERS.get(str(request.email).lower())
    if not user or request.password != user["password"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": _token(str(request.email).lower()), "user": {"email": str(request.email).lower(), "name": user["name"], "role": user["role"]}}


@router.get("/auth/me")
def me(authorization: str | None = Header(default=None)) -> dict:
    expected = f"Bearer {_token('demo@placementpulse.com')}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"email": "demo@placementpulse.com", "name": "Demo Student", "role": "student"}


@router.get("/dashboard/summary")
def dashboard_summary(authorization: str | None = Header(default=None)) -> dict:
    me(authorization)
    return {"readinessScore": 78, "readinessLevel": "Promising", "predictions": 3, "profileCompletion": 64, "focusAreas": ["Build one stronger project", "Practice aptitude in short sprints"], "recentActivity": [{"label": "Readiness check completed", "date": "Today"}, {"label": "Profile started", "date": "Yesterday"}]}
