# Data layout

Keep data sources isolated:

- `baseline/`: approved historical training data such as `Placement_Data_Full_Class.csv`.
- `synthetic/`: controlled development and robustness experiments only.
- `external/`: independently collected labelled records for evaluation only.

Do not merge external records into baseline training until outcome verification, privacy checks, duplicate checks, and leakage checks are complete.
