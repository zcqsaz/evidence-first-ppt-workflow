from pathlib import Path

from scripts.validate_pptx import validate_pptx
from scripts.common import resource_path, validate_json

from .conftest import make_config, make_deck


def test_valid_deck_passes(sample_project):
    report = validate_pptx(sample_project["deck"], sample_project["config"], sample_project["asset_root"])
    assert report["status"] == "pass"
    assert report["metrics"]["slide_count"] == 2
    assert report["metrics"]["crop_violation_count"] == 0
    assert report["metrics"]["out_of_bounds_count"] == 0
    assert report["metrics"]["text_overlap_count"] == 0
    assert report["metrics"]["asset_mapping"]["mapped_content_picture_hash_count"] == 1
    assert validate_json(report, resource_path("schemas/validation_report.schema.json")) == []


def test_bad_deck_detects_crop_duplicate_and_banned_phrase(sample_project):
    deck = sample_project["root"] / "bad.pptx"
    config = sample_project["root"] / "bad_config.json"
    make_deck(deck, sample_project["image"], bad=True)
    make_config(config, 3)
    report = validate_pptx(deck, config, sample_project["asset_root"])
    codes = {item["code"] for item in report["issues"] if item["severity"] == "error"}
    assert report["status"] == "fail"
    assert "NONZERO_PICTURE_CROP" in codes
    assert "DUPLICATE_EVIDENCE_MEDIA" in codes
    assert "BANNED_PHRASE" in codes
