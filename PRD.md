# Product Requirements Document

## Student Placement Prediction and Readiness Analysis

**Version:** 1.0  
**Date:** 2026-10-08  
**Status:** Proposed MVP  
**Source:** Mini project proposal, BMS Institute of Technology and Management

## 1. Product Summary

Build an educational decision-support application that estimates whether a student profile resembles historically placed or non-placed profiles and explains the main factors behind that estimate. The product will accept structured student data and supported resume or placement-form uploads. It will use a leakage-aware machine-learning pipeline, provide readiness-oriented feedback, and preserve a clean separation between training data and independently collected external evaluation data.

The system must clearly communicate that its output is an estimate, not a guarantee of employment or a replacement for interviews, recruiter judgment, or institutional placement policy.

## 2. Problem Statement

Students often receive fragmented feedback about academics, aptitude, coding, projects, internships, certifications, and technical skills. Placement coordinators also need to review large numbers of student records and resumes. A single, understandable tool can combine these pre-placement indicators, identify areas for improvement, and support earlier intervention.

The underlying technical challenge is to create a reproducible classifier that handles numerical, categorical, and document-derived data without target leakage, while remaining useful and understandable to non-technical users.

## 3. Goals and Success Criteria

### Goals

- Predict `Placed` or `Not Placed` from valid pre-placement attributes.
- Show an estimated probability and/or readiness level with appropriate caveats.
- Explain the strongest factors associated with the prediction.
- Provide practical improvement suggestions tied to weaker indicators.
- Support manual entry and resume/form-assisted entry.
- Compare Logistic Regression, Decision Tree, Random Forest, and SVM models.
- Evaluate internal performance separately from independent external performance.
- Create a controlled path for validated records to support future retraining.

### Success criteria

- A user can complete a valid manual prediction in under a few minutes.
- A valid prediction is returned within a few seconds after submission.
- The same valid input produces the same result for a fixed model version.
- All model candidates are reported using accuracy, precision, recall, F1 score, and confusion matrix.
- No identifier, salary, or post-placement field is used as a prediction feature.
- Uploaded-document fields are shown for user confirmation before inference.
- External evaluation data is not used for tuning the deployed experiment.
- Users can identify at least one actionable improvement area from the result.

## 4. Target Users

### Primary: Students

Students who want an early, understandable view of their placement readiness and areas to improve.

### Secondary: Placement coordinators

Coordinators who want consistent profile analysis, document-assisted data entry, and aggregate insight for student support.

### Explicitly out of scope as users

Recruiters using the system to automatically rank or reject candidates, admissions teams, or any workflow that treats the prediction as a final employment decision.

## 5. Product Principles and Guardrails

- **Pre-placement only:** Use information available before the relevant placement outcome.
- **Leakage-aware:** Exclude `salary`, serial numbers, identifiers, and any outcome-dependent field.
- **Human verification:** Never silently trust ambiguous OCR/NLP extraction.
- **Decision support:** Present estimates and contributing factors, not guarantees or judgments of personal worth.
- **Traceability:** Retain dataset source, collection period, validation status, and model version.
- **Privacy by design:** Minimize personal information and avoid retaining raw documents unless explicitly required.
- **Fairness awareness:** Report limitations caused by institution-specific and historically biased data; do not imply universal validity.

## 6. Scope

### MVP in scope

1. Load the local campus-placement dataset (`Placement_Data_Full_Class.csv`) containing approximately 215 records.
2. Clean and validate data using a reusable preprocessing pipeline.
3. Exclude leakage-prone and identifying fields.
4. Train and compare four classical classification models.
5. Use stratified train/test splitting and cross-validation.
6. Provide a React-based web interface for manual profile entry.
7. Provide resume/form upload with OCR/NLP extraction for supported PDF/image documents.
8. Require user confirmation of extracted values.
9. Display prediction, probability/readiness, contributing factors, and suggestions.
10. Keep synthetic and external data streams separate from the baseline training set.
11. Produce an evaluation report covering internal and, where labels exist, external results.

### Future scope

- Institution-level dashboards and cohort trends.
- Role-specific recommendations and recruiter requirement matching.
- Automated retraining workflow after outcome verification.
- More advanced models or embeddings after the classical baseline is validated.
- Authentication, multi-tenant data management, and production-grade document storage.

## 7. User Journeys

### Journey A: Manual prediction

1. Student opens the application.
2. Student enters academic, employability, technical, coding, project, internship, and certification details.
3. Application validates required fields, ranges, and categories.
4. Student submits the profile.
5. System applies the saved preprocessing pipeline and model.
6. System shows placement estimate, readiness information, influencing factors, and suggestions.

### Journey B: Resume/form-assisted prediction

1. User uploads a supported PDF or image.
2. OCR converts the document to text.
3. NLP extraction identifies relevant sections and values.
4. System highlights low-confidence or ambiguous fields.
5. User reviews and corrects extracted values.
6. System validates the confirmed profile and runs the same prediction pipeline as manual entry.

### Journey C: Coordinator evaluation

1. Coordinator loads an approved external evaluation file.
2. System maps records to the common schema and checks quality.
3. Records remain outside training and tuning data.
4. Once actual outcomes are available, the system calculates external metrics.
5. Only validated, de-duplicated, privacy-checked records may be considered for a future training cycle.

## 8. Functional Requirements

### FR-1: Profile input

The system shall accept, where available:

- SSC and HSC percentages, board, and stream.
- Degree percentage and degree type.
- Work experience and internship indicators.
- Employability or aptitude-test score.
- MBA specialization and percentage.
- Programming languages, frameworks, and tools.
- Project count, domains, and technologies.
- Certification count and categories.
- Coding-platform activity such as problems solved, rank, rating, or score.

### FR-2: Validation

The system shall validate numeric ranges, categorical values, required fields, missing values, duplicate records, and unsupported document fields. It shall show clear correction messages and shall not infer a value when the input is invalid or ambiguous.

### FR-3: Document extraction

The system shall accept supported PDF/image resumes or forms, perform OCR where needed, extract relevant candidate fields, normalize them to the common schema, attach extraction confidence, and require confirmation before prediction.

### FR-4: Preprocessing

The system shall use the same saved preprocessing logic for training, manual inputs, and confirmed document-derived inputs. This includes missing-value handling, categorical encoding, and numeric scaling where required.

### FR-5: Model training and comparison

The training workflow shall support Logistic Regression, Decision Tree, Random Forest, and Support Vector Machine classifiers. It shall record model configuration, feature schema, dataset source, split strategy, and model version.

### FR-6: Evaluation

The system shall report accuracy, precision, recall, F1 score, and confusion matrix. Internal validation results shall be reported separately from independent external evaluation results. Model selection shall consider balanced and stable performance rather than accuracy alone.

### FR-7: Prediction result

The result shall contain:

- Predicted class: `Placed` or `Not Placed`.
- Estimated probability when supported by the model.
- A readiness level with documented thresholds or interpretation rules.
- Important positive and negative contributing factors.
- Basic suggestions mapped to weaker indicators.
- Model version and a disclaimer that the output is not a guarantee.

### FR-8: Data separation and traceability

The system shall retain source and collection metadata. Baseline training data, synthetic experimentation data, and real-world external evaluation data shall remain distinguishable. External records shall not enter retraining until outcome verification, privacy checks, duplicate checks, and leakage checks are complete.

## 9. Feature and Data Specification

| Group | Examples | Use |
|---|---|---|
| Academic | `ssc_p`, `hsc_p`, `degree_p`, `mba_p`, degree type | Pre-placement academic indicators |
| Background | Board, stream, degree type, specialization | Categorical context |
| Employability | Employability test, aptitude score, work experience | Readiness indicators |
| Coding | Problems solved, rank, rating, score | Technical practice indicators |
| Skills | Languages, frameworks, tools | Technical profile |
| Experience | Internships, duration, projects | Applied experience |
| Certifications | Count and categories | Skill-validation indicators |
| Document-derived | Education, skills, projects, internships, certifications | Extracted after confirmation |
| Excluded | `sl_no`, identifiers, `salary`, post-placement fields | Must not enter prediction |
| Target | `status`: Placed / Not Placed | Supervised-learning label |

## 10. Readiness Analysis

Readiness must be framed as a transparent interpretation layer over validated inputs and model output. It should not create unsupported causal claims. Suggestions should be simple and rule-based for the MVP, for example:

- Low academic indicator: suggest targeted academic or subject revision.
- Low aptitude/employability score: suggest timed aptitude practice.
- Limited coding activity: suggest a structured problem-solving plan.
- Few projects: suggest completing and documenting a relevant project.
- Limited experience or certifications: suggest an appropriate internship, certification, or portfolio activity.

Suggestions must state that improvement may help but cannot guarantee placement.

## 11. Non-Functional Requirements

- **Usability:** A student or coordinator should understand the form and result without ML expertise.
- **Performance:** Manual prediction should complete within a few seconds on the target laptop.
- **Reliability:** Fixed inputs and a fixed model version must produce deterministic results.
- **Maintainability:** Separate data ingestion, preprocessing, training, evaluation, inference, extraction, and UI modules.
- **Portability:** Run on Windows, Linux, or macOS with Python 3.x.
- **Resource target:** Support a 64-bit machine with 4 GB RAM minimum and 8 GB recommended.
- **Privacy:** Avoid unnecessary personal data collection and clearly explain document handling.
- **Accessibility:** Use plain language, readable labels, visible validation messages, and non-color-only status cues.

## 12. Technical Architecture

1. **Data layer:** baseline CSV, synthetic dataset, and isolated external-evaluation dataset.
2. **Schema/validation layer:** canonical feature names, types, ranges, missing-value policy, and source metadata.
3. **Preprocessing layer:** fitted encoders/scalers and leakage exclusion rules.
4. **Model layer:** candidate classifiers, cross-validation, metric reporting, and serialized selected model.
5. **Document layer:** OCR, section detection, field extraction, confidence flags, and user confirmation.
6. **Interpretation layer:** probability/readiness calculation, factor presentation, and suggestion rules.
7. **Application layer:** React web interface for input, upload/review, prediction, evaluation, and limitations.

## 12.1 Technology Stack

### Software stack

| Area | Technology / Requirement |
|---|---|
| Programming language | Python 3.x for data processing, machine learning, OCR/NLP integration, and backend services |
| Data processing | Pandas, NumPy |
| Machine learning | Scikit-learn |
| Visualization and analysis | Matplotlib and Seaborn |
| Model persistence | Joblib |
| OCR and NLP | Suitable OCR/NLP libraries for extracting fields from supported resumes and placement forms |
| Frontend / web interface | React |
| Development tools | Jupyter Notebook and/or Visual Studio Code |
| Training dataset | `Placement_Data_Full_Class.csv` |
| Experimentation data | Synthetic dataset |
| Evaluation data | Independently collected external evaluation data |

### Hardware and operating system

| Area | Requirement |
|---|---|
| Hardware | 64-bit laptop or desktop |
| Memory | Minimum 4 GB RAM; 8 GB recommended |
| Operating system | Windows, Linux, or macOS |

## 13. MVP Acceptance Criteria

- [ ] A clean training run completes from the approved baseline dataset.
- [ ] `salary`, identifiers, and post-placement fields are absent from the model feature matrix.
- [ ] All four required classifiers train successfully or a documented dependency limitation is recorded.
- [ ] Stratified validation and cross-validation results are reproducible.
- [ ] Accuracy, precision, recall, F1, and confusion matrices are available for comparison.
- [ ] Manual input can produce a prediction using the saved pipeline.
- [ ] Invalid and missing inputs produce understandable correction guidance.
- [ ] Resume/form extraction displays extracted values for confirmation before prediction.
- [ ] Prediction results include class, probability/readiness interpretation, factors, suggestions, model version, and disclaimer.
- [ ] Synthetic and external records are not silently mixed into baseline training.
- [ ] The application runs through the documented setup and launch instructions.

## 14. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Small baseline dataset | Overfitting and unstable estimates | Cross-validation, conservative claims, external evaluation |
| Institution-specific bias | Poor generalization | Separate external test set and report cohort limitations |
| Target leakage | Unrealistically high metrics | Explicit feature allowlist and leakage checks |
| OCR/NLP errors | Incorrect predictions | Confidence flags and mandatory user confirmation |
| Synthetic-data overuse | Misleading robustness claims | Use synthetic data for controlled experiments only |
| Class imbalance | Misleading accuracy | Report precision, recall, F1, and confusion matrix |
| Sensitive personal data | Privacy harm | Minimize fields, avoid unnecessary retention, document handling policy |
| Misinterpretation as hiring decision | User harm | Strong disclaimers, no ranking/rejection workflow, human oversight |

## 15. Measurement and Reporting

The project report should include:

- Dataset inventory and feature schema.
- Missing-value and preprocessing decisions.
- Explicit leakage audit.
- Internal split and cross-validation strategy.
- Model comparison table with all required metrics.
- Confusion matrices.
- Baseline versus expanded-feature comparison where feasible.
- External evaluation results and cohort metadata.
- Examples of extracted fields and correction flow.
- Limitations, fairness considerations, and responsible-use statement.

## 16. Release Definition

The MVP is ready for demonstration when a user can enter or confirm a student profile, receive an explainable placement estimate and readiness guidance, and the team can show reproducible evaluation evidence without mixing leakage-prone or unvalidated data into training.

## 17. Open Decisions

- Exact readiness-level names and probability thresholds.
- Supported document formats and OCR engine.
- Whether raw uploaded documents are discarded immediately or retained with explicit consent.
- Minimum completeness required for a prediction.
- Final model-selection rule when metrics disagree.
- Whether external evaluation is implemented as a file upload, database table, or both.
