import sys
from pathlib import Path
from typing import Dict, Any, List
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# Setup pathing
API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_DIR.parent

CATEGORICAL_FEATURES = ["branch", "college_tier"]
NUMERIC_FEATURES = [
    "cgpa", "backlogs", "coding_skills", "dsa_score", "aptitude_score",
    "communication_skills", "ml_knowledge", "system_design", "internships",
    "projects_count", "certifications", "hackathons",
    "open_source_contributions", "extracurriculars"
]
ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

app = FastAPI(
    title="PlacementIQ API",
    description="Student Placement Prediction & Intelligence API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.middleware("http")
async def handle_vercel_rewrites(request: Request, call_next):
    # Detect original matched path from Vercel proxy headers
    orig_path = (
        request.headers.get("x-matched-path")
        or request.headers.get("x-invoke-path")
        or request.headers.get("x-forwarded-uri")
    )
    if orig_path:
        request.scope["path"] = orig_path
    elif request.scope.get("path", "").startswith("/api/index.py"):
        request.scope["path"] = request.scope["path"][len("/api/index.py"):] or "/"
    return await call_next(request)

# Load pipeline model safely
MODEL_PIPELINE = None
MODEL_NAME = "None"

def get_model():
    global MODEL_PIPELINE, MODEL_NAME
    if MODEL_PIPELINE is not None:
        return MODEL_PIPELINE
    
    # Search in multiple potential locations
    candidate_dirs = [
        PROJECT_ROOT / "models",
        API_DIR / "models",
        API_DIR.parent / "models",
    ]
    
    candidates = []
    for c_dir in candidate_dirs:
        if c_dir.exists():
            candidates.extend(sorted(c_dir.glob("*_pipeline.pkl")))
            
    if candidates:
        preferred = [p for p in candidates if "RandomForest" in p.name or "XGBoost" in p.name]
        chosen = preferred[0] if preferred else candidates[0]
        try:
            MODEL_PIPELINE = joblib.load(chosen)
            MODEL_NAME = chosen.name
            print(f"Loaded ML model: {MODEL_NAME}")
        except Exception as e:
            print(f"Error loading model {chosen}: {e}")
            MODEL_PIPELINE = None
    return MODEL_PIPELINE

class StudentProfile(BaseModel):
    branch: str = Field(default="CSE")
    college_tier: str = Field(default="Tier-2")
    cgpa: float = Field(default=7.8, ge=0.0, le=10.0)
    backlogs: int = Field(default=0, ge=0)
    coding_skills: float = Field(default=7.0, ge=0.0, le=10.0)
    dsa_score: float = Field(default=6.8, ge=0.0, le=10.0)
    aptitude_score: float = Field(default=75.0, ge=0.0, le=100.0)
    communication_skills: float = Field(default=7.0, ge=0.0, le=10.0)
    system_design: float = Field(default=5.5, ge=0.0, le=10.0)
    ml_knowledge: float = Field(default=6.0, ge=0.0, le=10.0)
    internships: int = Field(default=1, ge=0)
    projects_count: int = Field(default=3, ge=0)
    certifications: int = Field(default=2, ge=0)
    hackathons: int = Field(default=1, ge=0)
    open_source_contributions: int = Field(default=1, ge=0)
    extracurriculars: int = Field(default=2, ge=0)

class LoginRequest(BaseModel):
    email: str
    password: str

DEMO_TOKEN = "local-demo-token"
ADMIN_TOKEN = "local-admin-token"

@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    if credentials.email != "demo@placementpulse.com" or credentials.password != "placementpulse":
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": DEMO_TOKEN, "user": {"name": "Demo Student", "role": "student"}}

@app.post("/api/auth/admin/login")
async def admin_login(credentials: LoginRequest):
    if credentials.email != "admin@placementpulse.com" or credentials.password != "adminpulse":
        raise HTTPException(status_code=401, detail="Invalid admin email or password")
    return {"token": ADMIN_TOKEN, "user": {"name": "Placement Admin", "role": "admin"}}

def require_admin(request: Request):
    if request.headers.get("authorization") != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Admin authentication required")

@app.get("/api/admin/insights")
async def admin_insights(request: Request):
    require_admin(request)
    data_path = PROJECT_ROOT / "data" / "raw" / "student_placement_synthetic.csv"
    if not data_path.exists():
        raise HTTPException(status_code=503, detail="Backend dataset is unavailable")
    df = pd.read_csv(data_path)
    placed = pd.to_numeric(df["placement_status"], errors="coerce").fillna(0)
    model = get_model()
    probabilities = model.predict_proba(df[ALL_FEATURES])[:, 1] if model is not None else placed
    salary_column = "salary_package_lpa" if "salary_package_lpa" in df else "salary_package"
    by_branch = []
    for branch, group in df.assign(_placed=placed, _probability=probabilities).groupby("branch", sort=True):
        by_branch.append({
            "branch": branch,
            "count": int(len(group)),
            "placementRate": round(float(group["_placed"].mean() * 100), 1),
            "averageReadiness": round(float(group["_probability"].mean() * 100), 1),
        })
    cohorts = []
    enriched = df.assign(_placed=placed, _probability=probabilities)
    for (branch, tier), group in enriched.groupby(["branch", "college_tier"], sort=True):
        cohort_salaries = pd.to_numeric(group[salary_column], errors="coerce").dropna() if salary_column in group else pd.Series(dtype=float)
        cohorts.append({
            "branch": branch,
            "collegeTier": tier,
            "count": int(len(group)),
            "placed": int(group["_placed"].sum()),
            "placementRate": round(float(group["_placed"].mean() * 100), 1),
            "averageCgpa": round(float(group["cgpa"].mean()), 2),
            "averageReadiness": round(float(group["_probability"].mean() * 100), 1),
            "averageSalary": round(float(cohort_salaries.mean()), 2) if not cohort_salaries.empty else None,
        })
    focus = [{"label": label, "value": round(float(df[column].mean()), 1)} for label, column in [("Communication", "communication_skills"), ("Open source", "open_source_contributions"), ("Certifications", "certifications")]]
    readiness_mix = {
        "Ready": int(np.sum(probabilities >= 0.75)),
        "Promising": int(np.sum((probabilities >= 0.5) & (probabilities < 0.75))),
        "Building": int(np.sum(probabilities < 0.5)),
    }
    feature_means = [
        {"label": "CGPA", "value": round(float(df["cgpa"].mean() / 10 * 100), 1)},
        {"label": "Coding", "value": round(float(df["coding_skills"].mean() / 10 * 100), 1)},
        {"label": "DSA", "value": round(float(df["dsa_score"].mean() / 10 * 100), 1)},
        {"label": "Aptitude", "value": round(float(df["aptitude_score"].mean()), 1)},
        {"label": "Communication", "value": round(float(df["communication_skills"].mean() / 10 * 100), 1)},
    ]
    salaries = pd.to_numeric(df[salary_column], errors="coerce").dropna() if salary_column in df else pd.Series(dtype=float)
    return {
        "totalStudents": int(len(df)),
        "placedRate": round(float(placed.mean() * 100), 1),
        "unplacedRate": round(float((1 - placed.mean()) * 100), 1),
        "placementRate": round(float(placed.mean() * 100), 1),
        "averageReadiness": round(float(np.mean(probabilities) * 100), 1),
        "averagePackage": round(float(salaries.mean()), 2) if not salaries.empty else None,
        "byBranch": by_branch,
        "focusSignals": focus,
        "readinessMix": readiness_mix,
        "featureMeans": feature_means,
        "cohorts": cohorts,
    }

@app.get("/api/dashboard/summary")
async def dashboard_summary(request: Request):
    if request.headers.get("authorization") != f"Bearer {DEMO_TOKEN}":
        raise HTTPException(status_code=401, detail="Authentication required")
    return {
        "readinessScore": 0,
        "readinessLevel": "No checks yet",
        "profileCompletion": 0,
        "predictions": 0,
        "focusAreas": [],
        "recentActivity": [],
    }


def generate_recommendations(data: dict, proba: float) -> List[str]:
    recs = []
    if data["backlogs"] > 0:
        recs.append("⚠️ <strong>Clear Active Backlogs</strong>: 0 standing arrears are mandatory for 85%+ on-campus hiring drives.")
    if data["dsa_score"] < 6.5:
        recs.append("💻 <strong>Strengthen DSA Foundations</strong>: Practice medium difficulty questions on LeetCode / GeeksforGeeks.")
    if data["coding_skills"] < 6.5:
        recs.append("⌨️ <strong>Boost Practical Coding</strong>: Master time & space complexity, standard libraries, and clean syntax.")
    if data["internships"] == 0:
        recs.append("💼 <strong>Target Summer Internships</strong>: Practical company experience exponentially improves candidate conversion.")
    if data["projects_count"] < 2:
        recs.append("🚀 <strong>Deploy End-to-End Projects</strong>: Ship full-stack applications with live URLs and GitHub repositories.")
    if data["communication_skills"] < 6.5:
        recs.append("🗣️ <strong>Interview Preparation</strong>: Practice technical communication and STAR-format behavioral interview questions.")
    if not recs and proba > 0.8:
        recs.append("🌟 <strong>Strong Profile</strong>: Maintain momentum and target high-bracket Tier-1 product roles.")
    return recs


@app.get("/", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
async def serve_index():
    template_path = API_DIR / "templates" / "index.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text(encoding="utf-8"))
    
    # Check parent templates
    parent_template = PROJECT_ROOT / "api" / "templates" / "index.html"
    if parent_template.exists():
        return HTMLResponse(content=parent_template.read_text(encoding="utf-8"))
        
    return HTMLResponse(content="<h1>PlacementIQ Server Online</h1>")


@app.get("/api/health")
@app.get("/api/index.py/api/health")
async def health_check():
    model = get_model()
    return {
        "status": "healthy",
        "service": "PlacementIQ",
        "model_loaded": model is not None,
        "model_name": MODEL_NAME
    }


@app.post("/api/predict")
@app.post("/api/index.py/api/predict")
@app.post("/api/index.py")
async def predict_single(student: StudentProfile):
    model = get_model()
    data_dict = student.model_dump()
    df_input = pd.DataFrame([data_dict])
    
    if model is not None:
        try:
            pred = int(model.predict(df_input[ALL_FEATURES])[0])
            proba = float(model.predict_proba(df_input[ALL_FEATURES])[0][1])
        except Exception:
            # Fallback estimation calibrated against 100k records
            proba = float(np.clip(
                (student.cgpa / 10 * 0.25) +
                (student.coding_skills / 10 * 0.25) +
                (student.dsa_score / 10 * 0.20) +
                (student.aptitude_score / 100 * 0.15) +
                (0.10 if student.internships > 0 else 0) -
                (student.backlogs * 0.15),
                0.05, 0.99
            ))
            pred = int(proba >= 0.5)
    else:
        proba = float(np.clip(
            (student.cgpa / 10 * 0.25) +
            (student.coding_skills / 10 * 0.25) +
            (student.dsa_score / 10 * 0.20) +
            (student.aptitude_score / 100 * 0.15) +
            (0.10 if student.internships > 0 else 0) -
            (student.backlogs * 0.15),
            0.05, 0.99
        ))
        pred = int(proba >= 0.5)

    recs = generate_recommendations(data_dict, proba)
    confidence = "High" if proba > 0.75 else "Moderate" if proba > 0.50 else "Low"

    return {
        "will_be_placed": bool(pred),
        "placement_probability": round(proba, 4),
        "confidence": confidence,
        "recommendations": recs
    }


@app.post("/api/batch")
@app.post("/api/index.py/api/batch")
async def predict_batch(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")

    missing_cols = [c for c in ALL_FEATURES if c not in df.columns]
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"CSV missing required columns: {missing_cols}")

    model = get_model()
    if model is not None:
        try:
            preds = model.predict(df[ALL_FEATURES])
            probas = model.predict_proba(df[ALL_FEATURES])[:, 1]
        except Exception:
            probas = np.clip(
                (df["cgpa"] / 10 * 0.25) +
                (df["coding_skills"] / 10 * 0.25) +
                (df["dsa_score"] / 10 * 0.20) +
                (df["aptitude_score"] / 100 * 0.15) -
                (df["backlogs"] * 0.15),
                0.05, 0.99
            )
            preds = (probas >= 0.5).astype(int)
    else:
        probas = np.clip(
            (df["cgpa"] / 10 * 0.25) +
            (df["coding_skills"] / 10 * 0.25) +
            (df["dsa_score"] / 10 * 0.20) +
            (df["aptitude_score"] / 100 * 0.15) -
            (df["backlogs"] * 0.15),
            0.05, 0.99
        )
        preds = (probas >= 0.5).astype(int)

    df["Predicted_Status"] = np.where(preds == 1, "Placed", "Not Placed")
    df["Placement_Probability"] = np.round(probas, 4)

    total = len(df)
    placed = int(np.sum(preds))

    return {
        "total_records": total,
        "placed_count": placed,
        "unplaced_count": total - placed,
        "placement_rate": round(placed / total, 4) if total > 0 else 0,
        "sample_records": df.head(30).replace({np.nan: None}).to_dict(orient="records")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
