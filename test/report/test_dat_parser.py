from pathlib import Path

from coral.report.dat_parser import dat_parser


def test_dat_parser_reads_fixture_and_prints_results() -> None:
    fixture_path = Path(__file__).parent / "fixture" / "coverage.dat"
    entries = dat_parser(str(fixture_path))

    assert entries
    assert len(entries) == 17

    for entry in entries:
        print(f"file: {entry.file}")
        print(f"line: {entry.line}")
        print(f"column: {entry.column}")
        print(f"type: {entry.type.value}")
        print(f"page: {entry.page}")
        print(f"object: {entry.object}")
        print(f"hierarchy: {entry.hierarchy}")
        print(f"hits: {entry.hits}")
