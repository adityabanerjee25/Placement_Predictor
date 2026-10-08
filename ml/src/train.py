"""Train the candidate models. This script creates artifacts but does not wire them into the API."""

import argparse
import json
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from .preprocessing import build_preprocessor
from .schema import TARGET, model_columns
from .validation import load_and_validate


def train(path: str, artifact_dir: str) -> dict:
    frame, report = load_and_validate(path)
    features = model_columns(list(frame.columns))
    x, y = frame[features], frame[TARGET]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, stratify=y, random_state=42)
    candidates = {
        "logistic-regression": LogisticRegression(max_iter=2000),
        "decision-tree": DecisionTreeClassifier(random_state=42),
        "random-forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "svm": SVC(probability=True, random_state=42),
    }
    results = {}
    best_name, best_f1, best_pipeline = None, -1, None
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    for name, classifier in candidates.items():
        pipeline = Pipeline([("preprocess", build_preprocessor(x_train)), ("model", classifier)])
        pipeline.fit(x_train, y_train)
        predicted = pipeline.predict(x_test)
        metrics = {
            "accuracy": accuracy_score(y_test, predicted),
            "precision": precision_score(y_test, predicted, pos_label="Placed", zero_division=0),
            "recall": recall_score(y_test, predicted, pos_label="Placed", zero_division=0),
            "f1": f1_score(y_test, predicted, pos_label="Placed", zero_division=0),
            "confusionMatrix": confusion_matrix(y_test, predicted).tolist(),
            "crossValidationF1": cross_val_score(pipeline, x_train, y_train, cv=cv, scoring="f1_weighted").mean(),
        }
        results[name] = metrics
        if metrics["f1"] > best_f1:
            best_name, best_f1, best_pipeline = name, metrics["f1"], pipeline
    output = Path(artifact_dir)
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, output / "placement_model.joblib")
    (output / "feature_schema.json").write_text(json.dumps({"features": features, "target": TARGET}, indent=2))
    metadata = {"modelName": best_name, "modelVersion": f"{best_name}-v1", "rows": report.rows, "metrics": results}
    (output / "model_metadata.json").write_text(json.dumps(metadata, indent=2))
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument("--artifacts", default="ml/artifacts")
    args = parser.parse_args()
    print(json.dumps(train(args.dataset, args.artifacts), indent=2))
