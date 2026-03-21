from pathlib import Path

from coral.report.dat_parser import dat_parser
from coral.report.statistics import construct_coverage_hierarchy
from coral.report.write_report import write_report


def test_write_html_report() -> None:
    fixture_path = Path(__file__).parent / "fixture" / "coverage.dat"
    points = dat_parser(str(fixture_path))
    root = construct_coverage_hierarchy(points)

    output_dir = Path("test_output/html_report")
    write_report(root, output_dir)

    index_path = output_dir / "index.html"
    modules_dir = output_dir / "modules"
    top_module_path = modules_dir / "top.html"
    sub_module_path = modules_dir / "top.sub0.html"

    assert index_path.exists()
    assert modules_dir.exists()
    assert top_module_path.exists()
    assert sub_module_path.exists()

    index_content = index_path.read_text(encoding="utf-8")
    top_content = top_module_path.read_text(encoding="utf-8")
    sub_content = sub_module_path.read_text(encoding="utf-8")

    assert "Coverage Report" in index_content
    assert "top" in index_content
    assert "Module report page" in top_content
    assert "top.sub*" in sub_content
