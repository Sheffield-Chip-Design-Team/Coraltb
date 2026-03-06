from pathlib import Path

from coral.report.dat_parser import dat_parser
from coral.report.statistics import construct_coverage_hierarchy
from coral.report.write_md import coverage_module_to_markdown, write_coverage_markdown


def test_coverage_module_to_markdown_and_write() -> None:
    fixture_path = Path(__file__).parent / "fixture" / "coverage.dat"
    points = dat_parser(str(fixture_path))
    root = construct_coverage_hierarchy(points)

    markdown = coverage_module_to_markdown(root, input_name="coverage.dat")
    print(markdown)

    assert "# Coverage Report" in markdown
    assert "## Summary" in markdown
    assert "## Modules" in markdown
    assert "### Tree (hierarchy)" in markdown
    assert "## Module: top" in markdown
    assert "## Module: top.sub" in markdown

    output_path = Path("test_output/report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    written_path = write_coverage_markdown(root, str(output_path), input_name="coverage.dat")

    assert written_path == str(output_path)
    assert output_path.exists()
    written_content = output_path.read_text(encoding="utf-8")
    assert written_content == markdown

