from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas import Profile

router = APIRouter()
records: list[dict] = []


class ExternalEvaluation(BaseModel):
    profile: Profile
    outcome: str | None = Field(default=None, pattern="^(Placed|Not Placed)$")
    institution: str = Field(min_length=1, max_length=120)
    collectionPeriod: str = Field(min_length=1, max_length=40)
    source: str = Field(min_length=1, max_length=120)


@router.post("/external-evaluations", status_code=201)
def add_external_evaluation(record: ExternalEvaluation) -> dict:
    if any(item["profile"] == record.profile.model_dump() and item["institution"] == record.institution for item in records):
        raise HTTPException(status_code=409, detail="Duplicate external evaluation record.")
    item = {**record.model_dump(), "profile": record.profile.model_dump(), "status": "evaluation_only", "createdAt": datetime.now(timezone.utc).isoformat()}
    records.append(item)
    return {"recordId": len(records), "status": "evaluation_only"}


@router.get("/external-evaluations")
def list_external_evaluations() -> dict:
    return {"count": len(records), "records": records}
