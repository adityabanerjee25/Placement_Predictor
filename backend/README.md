# PlacementPulse backend

## Local setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`, with interactive docs at `/docs`.

The backend currently uses `MockPredictor` intentionally. PDF uploads receive lightweight text extraction and review flags; image OCR and the real model remain separate follow-up integrations. External records are stored in an evaluation-only in-memory repository and are never added to training.
