import pandas as pd
from pathlib import Path
from tempfile import TemporaryDirectory

from ml.src.train import train


def test_training_writes_artifacts():
    rows = []
    for index in range(30):
        rows.append({
            "ssc_p": 60 + index % 30,
            "hsc_p": 60 + index % 30,
            "degree_p": 60 + index % 30,
            "degree_t": "Sci&Tech" if index % 2 else "Comm&Mgmt",
            "workex": "Yes" if index % 3 == 0 else "No",
            "etest_p": 60 + index % 30,
            "specialisation": "Mkt&HR",
            "mba_p": 60 + index % 30,
            "sl_no": index,
            "salary": 300000 if index % 2 else None,
            "status": "Placed" if index % 2 else "Not Placed",
        })
    with TemporaryDirectory(dir=Path.cwd()) as directory:
        root = Path(directory)
        path = root / "training.csv"
        pd.DataFrame(rows).to_csv(path, index=False)
        metadata = train(str(path), str(root / "artifacts"))
        assert metadata["modelName"] in {"logistic-regression", "decision-tree", "random-forest", "svm"}
        assert (root / "artifacts" / "placement_model.joblib").exists()
        assert (root / "artifacts" / "model_metadata.json").exists()
