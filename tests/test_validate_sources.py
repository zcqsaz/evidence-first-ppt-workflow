from scripts.common import resource_path, validate_json
from scripts.validate_sources import validate_sources

from .conftest import make_metadata


def test_valid_sources_pass(sample_project):
    report = validate_sources(sample_project["metadata"], sample_project["asset_root"])
    assert report["status"] == "pass"
    assert report["metrics"]["files_found"] == 1
    assert report["metrics"]["unique_file_hashes"] == 1
    assert validate_json(report, resource_path("schemas/validation_report.schema.json")) == []


def test_unverified_and_missing_asset_fail(sample_project):
    metadata = sample_project["asset_root"] / "bad_metadata.csv"
    make_metadata(metadata, "missing.png", "0" * 64, valid=False)
    report = validate_sources(metadata, sample_project["asset_root"])
    codes = {item["code"] for item in report["issues"] if item["severity"] == "error"}
    assert report["status"] == "fail"
    assert "ASSET_NOT_FOUND" in codes
    assert "UNVERIFIED_ASSET" in codes
