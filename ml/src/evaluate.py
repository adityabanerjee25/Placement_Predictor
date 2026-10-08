"""Evaluate an already-selected artifact on an independent labelled dataset."""

import argparse
import json

import joblib
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from .schema import TARGET, model_columns
from .validation import load_and_validate


def evaluate(model_path: str, dataset_path: str) -> dict:
    frame, report = load_and_validate(dataset_path)
    x = frame[model_columns(list(frame.columns))]
    y = frame[TARGET]
    model = joblib.load(model_path)
    predicted = model.predict(x)
    return {
        "datasetRows": report.rows,
        "accuracy": accuracy_score(y, predicted),
        "precision": precision_score(y, predicted, pos_label="Placed", zero_division=0),
        "recall": recall_score(y, predicted, pos_label="Placed", zero_division=0),
        "f1": f1_score(y, predicted, pos_label="Placed", zero_division=0),
        "confusionMatrix": confusion_matrix(y, predicted).tolist(),
        "evaluationType": "external",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("dataset")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.model, args.dataset), indent=2))
