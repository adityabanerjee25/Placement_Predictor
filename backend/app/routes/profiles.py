from fastapi import APIRouter

from app.schemas import FieldDefinition, SchemaResponse, ValidationRequest, ValidationResponse

router = APIRouter()

FIELDS = [
    FieldDefinition(name="ssc_p", label="SSC percentage", type="number", required=True, min=0, max=100),
    FieldDefinition(name="hsc_p", label="HSC percentage", type="number", required=True, min=0, max=100),
    FieldDefinition(name="degree_p", label="Degree percentage", type="number", required=True, min=0, max=100),
    FieldDefinition(name="degree_t", label="Degree type", type="select", required=True, options=["Sci&Tech", "Comm&Mgmt", "Others"]),
    FieldDefinition(name="workex", label="Work experience", type="select", required=True, options=["Yes", "No"]),
    FieldDefinition(name="etest_p", label="Employability test score", type="number", required=True, min=0, max=100),
    FieldDefinition(name="project_count", label="Project count", type="number", required=False, min=0),
    FieldDefinition(name="coding_problems_solved", label="Coding problems solved", type="number", required=False, min=0),
]


@router.get("/schema", response_model=SchemaResponse)
def schema() -> SchemaResponse:
    return SchemaResponse(fields=FIELDS)


@router.post("/profile/validate", response_model=ValidationResponse)
def validate(request: ValidationRequest) -> ValidationResponse:
    return ValidationResponse(valid=True, errors=[], normalizedProfile=request.profile)
