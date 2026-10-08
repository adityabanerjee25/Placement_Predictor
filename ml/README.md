# ML pipeline

The ML layer is deliberately offline until the final integration phase. It validates the dataset, builds the shared preprocessing pipeline, compares four classifiers, and writes versioned artifacts.

```powershell
..\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
..\.venv\Scripts\python.exe -m ml.src.train path\to\Placement_Data_Full_Class.csv --artifacts ml\artifacts
```

The generated artifact is not automatically consumed by the API. That remains the final model-wiring step.
