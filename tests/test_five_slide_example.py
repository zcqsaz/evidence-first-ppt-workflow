from pathlib import Path

from pptx import Presentation

from examples.five_slide_academic_demo.build_demo import build_deck
from scripts.validate_pptx import validate_pptx


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "examples" / "five_slide_academic_demo"


def test_five_slide_demo_is_editable_private_safe_and_valid(tmp_path):
    output = tmp_path / "five_slide_academic_demo.pptx"
    build_deck(output)

    report = validate_pptx(output, EXAMPLE_DIR / "demo_config.json")
    assert report["status"] == "pass"
    assert report["metrics"]["slide_count"] == 5
    assert report["metrics"]["embedded_picture_hash_count"] == 0
    assert all(item["centered"] for item in report["metrics"]["page_numbers"])

    properties = Presentation(output).core_properties
    metadata = "\n".join(
        [
            properties.title or "",
            properties.subject or "",
            properties.author or "",
            properties.last_modified_by or "",
            properties.comments or "",
        ]
    ).lower()
    assert "@" not in metadata
    assert "steve canny" not in metadata
    assert properties.author == "Evidence-First PPT Workflow contributors"
    assert properties.last_modified_by == "Evidence-First PPT Workflow contributors"
