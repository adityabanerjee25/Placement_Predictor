from dataclasses import dataclass

import pandas as pd

from .schema import BASELINE_COLUMNS, EXCLUDED_COLUMNS, TARGET


@dataclass
class DataQualityReport:
    rows: int
    columns: list[str]
    missing_required: list[str]
    excluded_present: list[str]
    duplicate_rows: int
    target_values: list[str]
    missing_target: bool

    @property
    def valid(self) -> bool:
        return not self.missing_required and not self.missing_target and self.rows > 0


def inspect_frame(frame: pd.DataFrame) -> DataQualityReport:
    missing_required = sorted(BASELINE_COLUMNS - set(frame.columns))
    excluded_present = sorted((EXCLUDED_COLUMNS - {TARGET}) & set(frame.columns))
    target_values = sorted(frame[TARGET].dropna().astype(str).unique().tolist()) if TARGET in frame else []
    return DataQualityReport(
        rows=len(frame),
        columns=list(frame.columns),
        missing_required=missing_required,
        excluded_present=excluded_present,
        duplicate_rows=int(frame.duplicated().sum()),
        target_values=target_values,
        missing_target=TARGET not in frame.columns,
    )


def load_and_validate(path: str) -> tuple[pd.DataFrame, DataQualityReport]:
    frame = pd.read_csv(path)
    report = inspect_frame(frame)
    if not report.valid:
        raise ValueError({"missingRequired": report.missing_required, "missingTarget": report.missing_target, "excludedPresent": report.excluded_present, "rows": report.rows})
    return frame.drop(columns=report.excluded_present, errors="ignore"), report
