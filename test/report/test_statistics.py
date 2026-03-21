from pathlib import Path

from coral.report.dat_parser import dat_parser
from coral.report.models import CoverageModule
from coral.report.statistics import construct_coverage_hierarchy


def _print_module_tree(module: CoverageModule, depth: int = 0) -> None: # magic recursion
    indent = "  " * depth
    label = module.hierarchy if module.hierarchy else module.name
    print(f"{indent}module: {label}")
    print(
        f"{indent}  line: {module.lines_hits}/{module.lines_total}, "
        f"toggle: {module.toggles_hits}/{module.toggles_total}, "
        f"branch: {module.branches_hits}/{module.branches_total}, "
        f"expr: {module.expr_hits}/{module.expr_total}"
    )
    print(f"{indent}  local_points: {len(module.children_points)}")

    for child in sorted(module.children_modules, key=lambda m: m.hierarchy):
        _print_module_tree(child, depth + 1)


def test_construct_coverage_hierarchy_prints_tree() -> None:
    fixture_path = Path(__file__).parent / "fixture" / "coverage.dat"
    points = dat_parser(str(fixture_path))
    root = construct_coverage_hierarchy(points)

    assert root.children_modules
    _print_module_tree(root)
