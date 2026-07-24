from pathlib import Path

import pytest
from PIL import Image

from scripts.init_project import initialize_project
from scripts.make_contact_sheet import make_contact_sheet
from scripts.render_formula import render_formula
from scripts.compare_files import compare_files


def test_initializer_refuses_existing_destination(tmp_path: Path):
    template = tmp_path / "template"
    template.mkdir()
    (template / "PROJECT.md").write_text("test", encoding="utf-8")
    destination = tmp_path / "project"
    initialize_project(destination, template)
    assert (destination / "PROJECT.md").is_file()
    assert (destination / "00_input" / "original").is_dir()
    assert (destination / "07_qa" / "renders_final").is_dir()
    with pytest.raises(FileExistsError):
        initialize_project(destination, template)


def test_formula_and_contact_sheet(tmp_path: Path):
    renders = tmp_path / "renders"
    renders.mkdir()
    formula = render_formula(r"\frac{\sum_{i=1}^{n} x_i}{n}", renders / "slide_001.png")
    Image.new("RGB", (1600, 900), "white").save(renders / "slide_002.png")
    output = make_contact_sheet(renders, tmp_path / "contact.jpg", columns=2)
    assert formula.stat().st_size > 0
    assert output.stat().st_size > 0


def test_compare_files(tmp_path: Path):
    approved = tmp_path / "approved.pptx"
    delivery = tmp_path / "delivery.pptx"
    approved.write_bytes(b"same-package")
    delivery.write_bytes(b"same-package")
    assert compare_files(approved, delivery)["identical"] is True
    delivery.write_bytes(b"changed-package")
    assert compare_files(approved, delivery)["identical"] is False
