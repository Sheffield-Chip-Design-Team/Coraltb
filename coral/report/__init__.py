from pathlib import Path

from coral.report.dat_parser import dat_parser
from coral.report.statistics import construct_coverage_hierarchy
from coral.report.write_report import write_report


def generate_report(dat_file: str | Path, output_path: str | Path) -> None:
    points = dat_parser(str(dat_file))
    root = construct_coverage_hierarchy(points)
    write_report(root, Path(output_path))


__all__ = ["generate_report"]
