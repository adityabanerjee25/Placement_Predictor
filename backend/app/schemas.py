from typing import Literal

from pydantic import BaseModel, Field, field_validator


DegreeType = Literal["Sci&Tech", "Comm&Mgmt", "Others"]
Source = Literal["manual", "document", "external"]


class Profile(BaseModel):
    ssc_p: float = Field(ge=0, le=100)
    hsc_p: float = Field(ge=0, le=100)
    degree_p: float = Field(ge=0, le=100)
    degree_t: DegreeType
    workex: Literal["Yes", "No"]
    etest_p: float = Field(ge=0, le=100)
    specialisation: str | None = None
    mba_p: float | None = Field(default=None, ge=0, le=100)
    internship_duration: int | None = Field(default=None, ge=0)
    project_count: int | None = Field(default=None, ge=0)
    certification_count: int | None = Field(default=None, ge=0)
    programming_languages: list[str] = Field(default_factory=list)
    frameworks_tools: list[str] = Field(default_factory=list)
    coding_problems_solved: int | None = Field(default=None, ge=0)
    coding_rating: float | None = Field(default=None, ge=0)

    @field_validator("programming_languages", "frameworks_tools")
    @classmethod
    def trim_items(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value.strip()]


class ValidationRequest(BaseModel):
    profile: Profile


class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str]
    normalizedProfile: Profile


class PredictionRequest(BaseModel):
    profile: Profile
    confirmed: bool = False
    source: Source = "manual"


class Factor(BaseModel):
    label: str
    direction: Literal["positive", "negative", "focus"]
    value: str


class Suggestion(BaseModel):
    title: str
    reason: str


class Readiness(BaseModel):
    level: str
    score: int = Field(ge=0, le=100)
    summary: str


class PredictionResponse(BaseModel):
    prediction: Literal["Placed", "Not Placed"]
    probability: float = Field(ge=0, le=1)
    readiness: Readiness
    factors: list[Factor]
    suggestions: list[Suggestion]
    disclaimer: str
    modelVersion: str


class FieldDefinition(BaseModel):
    name: str
    label: str
    type: str
    required: bool
    min: float | None = None
    max: float | None = None
    options: list[str] = Field(default_factory=list)


class SchemaResponse(BaseModel):
    fields: list[FieldDefinition]


class ExtractedField(BaseModel):
    name: str
    value: str | int | float | None
    confidence: float = Field(ge=0, le=1)
    needsReview: bool


class ExtractionResponse(BaseModel):
    documentId: str
    status: Literal["needs_review", "unsupported", "ready"]
    fields: list[ExtractedField]
