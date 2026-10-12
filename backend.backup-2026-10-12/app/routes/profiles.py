from fastapi import APIRouter

from app.schemas import FieldDefinition, SchemaResponse, ValidationRequest, ValidationResponse

router = APIRouter()

FIELDS = [
    FieldDefinition(name="ssc_p", label="SSC percentage", type="number", required=True, min=0, max=100),
    FieldDefinition(name="hsc_p", label="HSC percentage", type="number", required=True, min=0, max=100),
    FieldDefinition(name="cgpa", label="CGPA", type="number", required=True, min=0, max=10),
    FieldDefinition(name="branch", label="Branch", type="select", required=True, options=["CSE", "AIML", "ISE", "IT", "ECE", "EEE", "ME", "CE"]),
    FieldDefinition(name="workex", label="Work experience", type="select", required=True, options=["Yes", "No"]),
    FieldDefinition(name="etest_p", label="Employability test score", type="number", required=True, min=0, max=100),
    FieldDefinition(name="project_count", label="Project count", type="number", required=False, min=0),
    FieldDefinition(name="coding_problems_solved", label="Coding problems solved", type="number", required=False, min=0),
    FieldDefinition(name="certification_count", label="Certifications", type="number", required=False, min=0),
    FieldDefinition(name="hackathon_count", label="Hackathons", type="number", required=False, min=0),
    FieldDefinition(name="open_source_contributions", label="Open-source contributions", type="number", required=False, min=0),
    FieldDefinition(name="communication_level", label="Communication level", type="select", required=False, options=["Beginner", "Intermediate", "Advanced"]),
]


@router.get("/schema", response_model=SchemaResponse)
def schema() -> SchemaResponse:
    return SchemaResponse(fields=FIELDS)


@router.post("/profile/validate", response_model=ValidationResponse)
def validate(request: ValidationRequest) -> ValidationResponse:
    return ValidationResponse(valid=True, errors=[], normalizedProfile=request.profile)
