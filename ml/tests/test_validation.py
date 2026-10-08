import pandas as pd

from ml.src.validation import inspect_frame, load_and_validate


def test_leakage_fields_are_reported():
    report = inspect_frame(pd.DataFrame({"ssc_p": [80], "hsc_p": [75], "degree_p": [70], "degree_t": ["Sci&Tech"], "workex": ["No"], "etest_p": [65], "specialisation": ["Mkt&HR"], "mba_p": [70], "salary": [300000], "status": ["Placed"]}))
    assert "salary" in report.excluded_present
    assert report.valid


def test_target_is_required():
    report = inspect_frame(pd.DataFrame({"ssc_p": [80]}))
    assert not report.valid
    assert report.missing_target


def test_quality_report_accepts_baseline_shape():
    frame = pd.DataFrame({"ssc_p": [80], "hsc_p": [75], "degree_p": [70], "degree_t": ["Sci&Tech"], "workex": ["No"], "etest_p": [65], "specialisation": ["Mkt&HR"], "mba_p": [70], "status": ["Placed"]})
    report = inspect_frame(frame)
    assert report.valid
    assert report.rows == 1
