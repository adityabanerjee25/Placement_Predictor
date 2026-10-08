from ml.src.schema import EXCLUDED_COLUMNS, model_columns


def test_model_columns_remove_target_and_leakage_fields():
    columns = ["sl_no", "ssc_p", "salary", "status", "degree_t"]
    assert model_columns(columns) == ["ssc_p", "degree_t"]
    assert "salary" in EXCLUDED_COLUMNS
