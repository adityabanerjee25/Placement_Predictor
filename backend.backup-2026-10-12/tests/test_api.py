import pytest

from app.routes.health import health
from app.routes.predictions import predict
from app.routes.external import ExternalEvaluation, add_external_evaluation, records
from app.routes.auth import LoginRequest, login, me, dashboard_summary
from app.schemas import PredictionRequest, Profile
from fastapi import HTTPException

PROFILE = Profile(ssc_p=82, hsc_p=79, degree_p=76, degree_t="Sci&Tech", workex="No", etest_p=72, project_count=2, coding_problems_solved=140)

def test_health():
    assert health() == {"status": "ok", "predictionMode": "mock", "modelVersion": "mock-v1"}

def test_prediction_requires_confirmation():
    with pytest.raises(HTTPException) as error:
        predict(PredictionRequest(profile=PROFILE, confirmed=False))
    assert error.value.status_code == 422

def test_prediction_contract():
    response = predict(PredictionRequest(profile=PROFILE, confirmed=True))
    assert response.modelVersion == "mock-v1"
    assert response.prediction in {"Placed", "Not Placed"}
    assert 0 <= response.probability <= 1
    assert response.factors
    assert response.suggestions

def test_external_evaluation_is_isolated():
    records.clear()
    response = add_external_evaluation(ExternalEvaluation(profile=PROFILE, institution="Test Institute", collectionPeriod="2026", source="manual"))
    assert response["status"] == "evaluation_only"
    assert records[0]["status"] == "evaluation_only"

def test_demo_login_and_protected_dashboard():
    logged_in = login(LoginRequest(email="demo@placementpulse.com", password="placementpulse"))
    authorization = f"Bearer {logged_in['token']}"
    assert me(authorization)["role"] == "student"
    assert dashboard_summary(authorization)["readinessScore"] == 78
