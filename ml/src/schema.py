"""Canonical feature contract shared by ingestion and training."""

TARGET = "status"
EXCLUDED_COLUMNS = {"sl_no", "salary", "status", "id", "student_id"}
BASELINE_COLUMNS = {
    "ssc_p", "hsc_p", "degree_p", "degree_t", "workex", "etest_p",
    "specialisation", "mba_p",
}
OPTIONAL_COLUMNS = {
    "internship_duration", "project_count", "certification_count",
    "programming_languages", "frameworks_tools", "coding_problems_solved",
    "coding_rating",
}


def model_columns(columns: list[str]) -> list[str]:
    """Return deterministic input columns, never including target/leakage fields."""
    return [column for column in columns if column not in EXCLUDED_COLUMNS]
