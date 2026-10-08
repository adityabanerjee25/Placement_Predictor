# PlacementPulse Implementation Specification

**Source:** [PRD.md](E:\Hackathon\PlacementPredictor\PRD.md)  
**Version:** 1.0  
**Priority rule:** Build the product contract and user experience first. Wire the trained ML model last.

## 1. Objective

Build a React-based student placement readiness application with a Python backend that can later call a validated machine-learning model. The first usable version must work with deterministic mock predictions so the frontend, API, validation, document-review flow, and result experience can be developed independently of model training.

The final model is an implementation detail behind a stable prediction contract. Replacing mock inference with the trained model must not require a frontend rewrite.

## 2. Delivery Strategy

### Priority order

1. Project structure, design system, and local developer workflow.
2. Frontend landing page and core navigation.
3. Profile schema and validation rules.
4. Backend API with mock prediction service.
5. Manual profile intake flow.
6. Prediction result and readiness guidance screens.
7. Resume/form upload and extraction-review workflow.
8. Data ingestion and dataset-quality checks.
9. ML training and evaluation pipeline.
10. Replace mock inference with the selected serialized model.
11. External evaluation, hardening, privacy review, and release documentation.

### Why the model comes last

The model depends on a stable feature schema, validated input rules, and a known API response shape. Building those contracts first prevents model-specific assumptions from leaking into the UI and allows the complete product flow to be tested with fixtures before training is finished.

## 3. Target Architecture

```text
React frontend
  -> REST API / FastAPI backend
       -> validation + feature schema
       -> document extraction service
       -> prediction service interface
            -> mock predictor during early phases
            -> serialized sklearn model at final integration
       -> metadata / evaluation storage

Offline ML pipeline
  -> dataset validation
  -> leakage-aware preprocessing
  -> model comparison
  -> metrics and artifacts
  -> selected model package consumed by backend
```

## 4. Technology Stack

### Frontend

- React 19+
- Vite 8+
- JavaScript initially; TypeScript may be introduced only if the project grows beyond the MVP.
- CSS modules or the existing global CSS system; avoid adding a UI framework until a repeated component need is proven.
- Native `fetch` for API calls.
- React state and small local components for the MVP; add a state library only when cross-page state becomes necessary.
- Google Fonts: Benne, Manrope, and JetBrains Mono.

### Backend

- Python 3.x.
- FastAPI for HTTP endpoints and request validation.
- Uvicorn for local development server.
- Pydantic for API schemas and field validation.
- Python `logging` for request and processing diagnostics.
- SQLite for local metadata and evaluation records if persistence is needed in the MVP.
- `python-multipart` for document uploads.

### Data and model

- Pandas and NumPy for ingestion and feature preparation.
- Scikit-learn for preprocessing, Logistic Regression, Decision Tree, Random Forest, SVM, cross-validation, and metrics.
- Joblib for fitted preprocessing and model artifacts.
- Matplotlib and Seaborn for offline evaluation reports.
- OCR/NLP libraries selected behind an extraction adapter; the UI must not depend on a particular OCR vendor.

### Development and quality

- Jupyter Notebook for exploration only; production logic belongs in importable Python modules.
- Visual Studio Code or equivalent.
- npm scripts for frontend development and build.
- pytest for backend and model tests.
- ESLint for frontend linting when the project needs formal lint checks.
- Git with small, phase-based commits.

### Runtime target

- Windows, Linux, or macOS.
- 64-bit laptop or desktop.
- 4 GB RAM minimum; 8 GB recommended.

## 5. Repository Structure

```text
PlacementPredictor/
├─ PRD.md
├─ spec.md
├─ design.md
├─ frontend/
│  ├─ package.json
│  ├─ index.html
│  └─ src/
│     ├─ App.jsx
│     ├─ App.css
│     ├─ index.css
│     ├─ components/
│     ├─ pages/
│     ├─ lib/
│     │  └─ api.js
│     └─ fixtures/
├─ backend/
│  ├─ requirements.txt
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ config.py
│  │  ├─ schemas.py
│  │  ├─ routes/
│  │  ├─ services/
│  │  └─ repositories/
│  └─ tests/
├─ ml/
│  ├─ data/
│  ├─ notebooks/
│  ├─ src/
│  │  ├─ schema.py
│  │  ├─ validation.py
│  │  ├─ preprocessing.py
│  │  ├─ train.py
│  │  ├─ evaluate.py
│  │  └─ artifacts.py
│  ├─ reports/
│  └─ artifacts/
└─ data/
   ├─ baseline/
   ├─ synthetic/
   ├─ external/
   └─ README.md
```

## 6. Shared Feature Contract

The following canonical schema is shared by manual entry, document extraction, training, and inference. Frontend labels may be more friendly, but API and model field names remain stable.

| Field | Type | Required for MVP | Validation |
|---|---|---:|---|
| `ssc_p` | number | Yes | 0-100 |
| `hsc_p` | number | Yes | 0-100 |
| `degree_p` | number | Yes | 0-100 |
| `degree_t` | enum | Yes | Approved degree categories |
| `workex` | boolean/enum | Yes | Yes or No |
| `etest_p` | number | Yes | 0-100 |
| `specialisation` | enum/string | No | Controlled value or blank |
| `mba_p` | number | No | 0-100 |
| `internship_duration` | number | No | 0 or positive months |
| `project_count` | integer | No | 0 or positive |
| `certification_count` | integer | No | 0 or positive |
| `programming_languages` | string array | No | Normalized names |
| `frameworks_tools` | string array | No | Normalized names |
| `coding_problems_solved` | integer | No | 0 or positive |
| `coding_rating` | number | No | 0 or positive |
| `source` | enum | Yes | `manual`, `document`, `external` |

Excluded from prediction: `sl_no`, personal identifiers, salary, placement date, employer outcome fields, and any field known only after placement.

## 7. Backend Specification

### 7.1 API conventions

- Base path: `/api/v1`.
- JSON responses use `camelCase` at the frontend boundary only if needed; backend model fields remain explicit and documented.
- Validation failures return HTTP 422 with field-level errors.
- Unexpected processing failures return HTTP 500 with a safe user message and a server-side log entry.
- Every prediction response includes `modelVersion`, even when the value is `mock-v1`.
- No raw uploaded document is returned in an API response.

### 7.2 Endpoints

#### `GET /api/v1/health`

Returns service status and active prediction mode.

```json
{
  "status": "ok",
  "predictionMode": "mock",
  "modelVersion": "mock-v1"
}
```

#### `GET /api/v1/schema`

Returns the feature definitions, labels, allowed categories, ranges, and required fields used to render or validate the intake form.

#### `POST /api/v1/profile/validate`

Validates a profile without running inference.

```json
{
  "valid": true,
  "errors": [],
  "normalizedProfile": {}
}
```

#### `POST /api/v1/predictions`

Accepts a validated profile and returns the stable prediction contract.

Request:

```json
{
  "profile": {
    "ssc_p": 82,
    "hsc_p": 79,
    "degree_p": 76,
    "degree_t": "Sci&Tech",
    "workex": "No",
    "etest_p": 72,
    "project_count": 2,
    "coding_problems_solved": 140
  },
  "confirmed": true,
  "source": "manual"
}
```

Response:

```json
{
  "prediction": "Placed",
  "probability": 0.78,
  "readiness": {
    "level": "Promising",
    "score": 78,
    "summary": "You have a solid base with a few areas worth strengthening."
  },
  "factors": [
    { "label": "Degree performance", "direction": "positive", "value": "76%" },
    { "label": "Aptitude readiness", "direction": "positive", "value": "72%" },
    { "label": "Project depth", "direction": "focus", "value": "2 projects" }
  ],
  "suggestions": [
    { "title": "Build one stronger project", "reason": "Show depth with a deployed or well-documented project." }
  ],
  "disclaimer": "This is an estimate for learning and preparation, not a guarantee of employment.",
  "modelVersion": "mock-v1"
}
```

#### `POST /api/v1/documents/extract`

Accepts one supported PDF or image. Returns normalized candidate fields, confidence, and review status. This endpoint must not run a prediction.

```json
{
  "documentId": "local-doc-001",
  "status": "needs_review",
  "fields": [
    { "name": "degree_p", "value": 76, "confidence": 0.94, "needsReview": false },
    { "name": "project_count", "value": 2, "confidence": 0.61, "needsReview": true }
  ]
}
```

#### `POST /api/v1/external-evaluations`

Reserved for coordinator workflows. Stores approved records separately from training data and requires source metadata and known outcome status.

### 7.3 Backend service boundaries

- `ProfileService`: normalize and validate canonical profiles.
- `PredictionService`: call the active predictor interface and assemble the result.
- `MockPredictor`: deterministic fixture-based predictor for early UI work.
- `ModelPredictor`: loads the Joblib artifact at final integration.
- `DocumentService`: OCR/NLP adapter plus confidence flags.
- `EvaluationService`: metric and external-record handling.
- `SuggestionService`: rule-based suggestions independent of model implementation.

## 8. Frontend Specification

### 8.1 Screens

1. **Landing page:** Current implemented visual foundation from the attached reference design.
2. **Readiness intake:** Group fields into academics, employability, experience, skills, coding, and projects.
3. **Resume review:** Upload, extraction progress, editable values, confidence flags, and confirmation.
4. **Prediction result:** Placement estimate, readiness level, factors, suggestions, model version, and disclaimer.
5. **Coordinator evaluation:** Later phase; external dataset upload and evaluation summary.

### 8.2 Frontend component plan

- `AppShell`
- `Header`
- `PrimaryButton`
- `StepLabel`
- `ProfileForm`
- `FieldGroup`
- `FieldError`
- `DocumentDropzone`
- `ExtractionReviewTable`
- `ReadinessScoreCard`
- `FactorsList`
- `SuggestionCard`
- `Disclaimer`
- `FaqAccordion`
- `LoadingState`
- `ErrorState`

### 8.3 Frontend behavior

- Load field definitions from `/schema` when the intake flow is introduced.
- Validate immediately for obvious range errors and again on submit through the backend.
- Disable prediction submission while a request is in progress.
- Preserve the confirmed profile when navigating to results.
- Do not display a result until document-derived fields are explicitly confirmed.
- Show graceful loading, empty, validation, and server-error states.
- Use accessible labels, keyboard-focus styles, semantic headings, and non-color-only status cues.
- Keep the “estimate, not a guarantee” message visible on the results view.

## 9. Model Specification

### 9.1 Data sources

- Baseline: `Placement_Data_Full_Class.csv`.
- Synthetic: separate development and robustness experiments only.
- External: isolated evaluation records with source and collection metadata.

### 9.2 Training rules

- Remove identifiers, salary, and post-placement fields before any split.
- Use a single reproducible preprocessing pipeline for training and inference.
- Apply stratified train/test splitting.
- Use cross-validation on the training portion only.
- Keep external data untouched until model selection is complete.
- Record random seed, feature list, dataset source, collection period, and model version.

### 9.3 Candidate models

1. Logistic Regression.
2. Decision Tree.
3. Random Forest.
4. Support Vector Machine.

The selected model must be chosen using stable, balanced performance across accuracy, precision, recall, F1, and confusion matrix review. Accuracy alone is insufficient.

### 9.4 Artifacts

```text
ml/artifacts/
├─ preprocessing.joblib
├─ placement_model.joblib
├─ feature_schema.json
├─ model_metadata.json
└─ evaluation_report.json
```

`model_metadata.json` must include model name, version, training data source, feature list, metrics, training timestamp, and limitations.

### 9.5 Final integration

The backend should depend on this interface, regardless of predictor implementation:

```python
class Predictor:
    def predict(self, profile: dict) -> dict:
        """Return the stable prediction response fields."""
```

Early phases use `MockPredictor`. Final integration swaps in `ModelPredictor`, which loads the fitted preprocessing and model artifacts once at service startup and returns the same response shape.

## 10. Readiness and Suggestions

The MVP uses a transparent rule layer around validated inputs:

- Academic weakness -> academic revision suggestion.
- Aptitude/employability weakness -> timed practice suggestion.
- Low coding activity -> structured problem-solving plan.
- Few projects -> project-depth suggestion.
- Low experience/certification coverage -> portfolio, internship, or certification suggestion.

Rules must be documented, deterministic, and clearly presented as guidance. They must not claim that a single feature causes placement.

## 11. Systematic Implementation Plan

### Phase 0 - Foundation

**Deliverables:** repository structure, environment instructions, design tokens, frontend scripts, backend skeleton, shared schema draft.

**Exit criteria:** frontend builds, backend health endpoint responds, and the canonical schema is committed.

### Phase 1 - Frontend shell

**Deliverables:** landing page, navigation, responsive layout, shared buttons/cards/labels, design documentation.

**Exit criteria:** reference-inspired landing page works on desktop and mobile widths without backend dependency.

### Phase 2 - Backend contract

**Deliverables:** FastAPI app, CORS for local frontend, Pydantic schemas, health/schema/validate endpoints, error format, deterministic mock predictor.

**Exit criteria:** API can validate a profile and return the documented prediction response with `mock-v1`.

### Phase 3 - Manual intake and result flow

**Deliverables:** React form, grouped fields, client validation, API client, loading/error states, result page, readiness cards, suggestions, disclaimer.

**Exit criteria:** a user can complete the manual journey from landing page to result using mock inference.

### Phase 4 - Document-assisted flow

**Deliverables:** upload endpoint, OCR/NLP adapter, extraction response, editable review screen, confidence flags, confirmation gate.

**Exit criteria:** document-derived values cannot reach prediction until the user confirms them.

### Phase 5 - Data and quality pipeline

**Deliverables:** dataset loader, canonical schema mapper, missing-value policy, leakage audit, duplicate check, source metadata, synthetic/external separation.

**Exit criteria:** a clean data-quality report exists and no excluded feature reaches the model matrix.

### Phase 6 - Model development

**Deliverables:** reproducible training script, four candidate models, stratified split, cross-validation, metrics, confusion matrices, model artifact, metadata report.

**Exit criteria:** selected model is justified by documented metrics and limitations.

### Phase 7 - Model wiring

**Deliverables:** `ModelPredictor`, startup artifact loading, model version in responses, inference tests, mock-to-real configuration switch.

**Exit criteria:** frontend behavior is unchanged when the real model replaces `MockPredictor`.

### Phase 8 - External evaluation and release

**Deliverables:** isolated external evaluation route, outcome verification checks, privacy review, setup guide, demo script, final report.

**Exit criteria:** internal and external metrics are reported separately and the responsible-use guardrails are visible in the application.

## 12. Testing Strategy

### Frontend

- Build succeeds with `npm run build`.
- Manual smoke test for navigation, CTA, FAQ, form validation, loading, result, and mobile layout.
- Accessibility check for form labels, keyboard focus, buttons, and contrast.

### Backend

- Unit tests for numeric ranges, enums, missing values, exclusions, and normalization.
- API tests for 200, 422, and safe 500 responses.
- Contract test that mock and real predictors return the same response shape.
- Upload tests for supported, unsupported, oversized, and ambiguous documents.

### Model

- Assert excluded features are absent.
- Assert preprocessing is fitted only on training data.
- Assert fixed seed gives repeatable metrics.
- Assert serialized artifacts can be loaded and predict a valid profile.
- Report internal and external evaluation separately.

## 13. Configuration

Suggested backend environment values:

```text
PREDICTION_MODE=mock
MODEL_ARTIFACT_DIR=../ml/artifacts
MAX_UPLOAD_MB=5
ALLOWED_ORIGINS=http://localhost:5173
DATABASE_URL=sqlite:///./placementpulse.db
```

Use `PREDICTION_MODE=model` only after artifacts and model integration tests pass.

## 14. Definition of Done

- Frontend and backend run from documented commands.
- Manual flow works end-to-end with mock inference.
- Model-independent API contracts are stable and documented.
- Document extraction requires confirmation.
- Data sources remain separated.
- Leakage checks pass.
- Selected model is versioned and loadable.
- Real-model wiring requires no UI contract changes.
- Results show factors, suggestions, model version, and responsible-use disclaimer.
- Known limitations are included in the project report.

## 15. Risks to Track

- The baseline dataset is small and institution-specific; avoid broad claims.
- OCR quality may vary by document layout; confidence and confirmation are mandatory.
- Synthetic data must not be presented as proof of real-world generalization.
- Model probability may not be calibrated; label it as an estimate unless calibration is validated.
- Personal data handling must be defined before persistent uploads or coordinator workflows.

## 16. Deferred Work

- Authentication and role-based access.
- Production database and object storage.
- Automated retraining.
- Cohort dashboards and ranking-like views.
- Advanced deep-learning or LLM features.
- Deployment infrastructure and CI/CD beyond local MVP needs.
