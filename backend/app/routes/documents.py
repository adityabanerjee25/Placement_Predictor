from uuid import uuid4
import re
from io import BytesIO

from fastapi import APIRouter, File, UploadFile
from pypdf import PdfReader
from PIL import Image
import pytesseract

from app.schemas import ExtractedField, ExtractionResponse

router = APIRouter()
SUPPORTED = {"application/pdf", "image/png", "image/jpeg"}


@router.post("/documents/extract", response_model=ExtractionResponse)
async def extract(file: UploadFile = File(...)) -> ExtractionResponse:
    if file.content_type not in SUPPORTED:
        return ExtractionResponse(documentId="", status="unsupported", fields=[])
    content = await file.read()
    text = ""
    if file.content_type == "application/pdf":
        reader = PdfReader(BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        try:
            text = pytesseract.image_to_string(Image.open(BytesIO(content)))
        except (OSError, RuntimeError):
            text = ""
    degree = _first_number(text, r"degree(?:\s+percentage|\s+percent|\s*%)?\D{0,12}(\d{1,3}(?:\.\d+)?)")
    projects = _first_number(text, r"(?:projects?|project count)\D{0,12}(\d{1,2})")
    return ExtractionResponse(
        documentId=f"local-doc-{uuid4().hex[:8]}",
        status="needs_review",
        fields=[
            ExtractedField(name="degree_p", value=degree, confidence=0.65 if degree is not None else 0.0, needsReview=True),
            ExtractedField(name="project_count", value=projects, confidence=0.65 if projects is not None else 0.0, needsReview=True),
            ExtractedField(name="programming_languages", value=None, confidence=0.0, needsReview=True),
        ],
    )


def _first_number(text: str, pattern: str) -> float | int | None:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    return int(value) if value.is_integer() else value
