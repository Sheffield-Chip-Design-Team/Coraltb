from __future__ import annotations

from datetime import date

from coral.report.models import CoverageModule, CoveragePoint, CoverageType


def _percent(hit: int, total: int) -> str:
    if total <= 0:
        return "N/A"
    return f"{(hit / total) * 100:.1f}%"


def _anchor_for_module(module: CoverageModule) -> str:
    label = module.hierarchy or module.name or "root"
    return "module-" + label.replace(".", "-").replace("_", "-")


def _module_title(module: CoverageModule) -> str:
    return module.hierarchy or module.name or "root"


def _collect_modules(module: CoverageModule) -> list[CoverageModule]:
    items: list[CoverageModule] = []
    for child in module.children_modules:
        items.append(child)
        items.extend(_collect_modules(child))
    return items


def _aggregate(module: CoverageModule) -> tuple[int, int, int, int, int, int, int, int]:
    lines_total = module.lines_total
    lines_hits = module.lines_hits
    toggles_total = module.toggles_total
    toggles_hits = module.toggles_hits
    branches_total = module.branches_total
    branches_hits = module.branches_hits
    expr_total = module.expr_total
    expr_hits = module.expr_hits

    for child in module.children_modules:
        (
            child_lines_total,
            child_lines_hits,
            child_toggles_total,
            child_toggles_hits,
            child_branches_total,
            child_branches_hits,
            child_expr_total,
            child_expr_hits,
        ) = _aggregate(child)
        lines_total += child_lines_total
        lines_hits += child_lines_hits
        toggles_total += child_toggles_total
        toggles_hits += child_toggles_hits
        branches_total += child_branches_total
        branches_hits += child_branches_hits
        expr_total += child_expr_total
        expr_hits += child_expr_hits

    return (
        lines_total,
        lines_hits,
        toggles_total,
        toggles_hits,
        branches_total,
        branches_hits,
        expr_total,
        expr_hits,
    )


def _points_by_type(points: list[CoveragePoint], point_type: CoverageType) -> list[CoveragePoint]:
    return [point for point in points if point.type == point_type]


def _render_tree(module: CoverageModule, md_lines: list[str], indent: int = 0) -> None:
    spacing = "  " * indent
    (
        lines_total,
        lines_hits,
        toggles_total,
        toggles_hits,
        branches_total,
        branches_hits,
        _expr_total,
        _expr_hits,
    ) = _aggregate(module)

    md_lines.append(f"{spacing}<details>")
    md_lines.append(
        f"{spacing}  <summary>{_module_title(module)} "
        f"(line {_percent(lines_hits, lines_total)}, "
        f"branch {_percent(branches_hits, branches_total)}, "
        f"toggle {_percent(toggles_hits, toggles_total)})</summary>"
    )
    md_lines.append("")

    for child in sorted(module.children_modules, key=lambda item: item.hierarchy):
        _render_tree(child, md_lines, indent + 1)

    if module.children_points:
        md_lines.append(f"{spacing}  - local points: {len(module.children_points)}")

    md_lines.append(f"{spacing}</details>")


def _render_module_sections(module: CoverageModule, md_lines: list[str]) -> None:
    module_id = _anchor_for_module(module)
    md_lines.append(f"## Module: {_module_title(module)} {{#{module_id}}}")
    md_lines.append("")

    md_lines.append("### Local summary")
    md_lines.append("| Metric | Hit | Total | % |")
    md_lines.append("|--------|-----|-------|---|")
    md_lines.append(
        f"| Line | {module.lines_hits} | {module.lines_total} | {_percent(module.lines_hits, module.lines_total)} |"
    )
    md_lines.append(
        f"| Branch | {module.branches_hits} | {module.branches_total} | {_percent(module.branches_hits, module.branches_total)} |"
    )
    md_lines.append(
        f"| Toggle | {module.toggles_hits} | {module.toggles_total} | {_percent(module.toggles_hits, module.toggles_total)} |"
    )
    md_lines.append(
        f"| Expr | {module.expr_hits} | {module.expr_total} | {_percent(module.expr_hits, module.expr_total)} |"
    )
    md_lines.append("")

    toggles = _points_by_type(module.children_points, CoverageType.TOGGLE)
    md_lines.append("### Toggle")
    md_lines.append("| File | Line | Object | Count | Status |")
    md_lines.append("|------|------|--------|-------|--------|")
    for point in toggles:
        status = "OK" if point.hits > 0 else "Not reach"
        md_lines.append(
            f"| {point.file} | {point.line} | {point.object} | {point.hits} | {status} |"
        )
    if not toggles:
        md_lines.append("| - | - | - | - | - |")
    md_lines.append("")

    branches = _points_by_type(module.children_points, CoverageType.BRANCH)
    md_lines.append("### Branch")
    md_lines.append("| File | Line | Kind | Count |")
    md_lines.append("|------|------|------|-------|")
    for point in branches:
        md_lines.append(f"| {point.file} | {point.line} | {point.object} | {point.hits} |")
    if not branches:
        md_lines.append("| - | - | - | - |")
    md_lines.append("")


def coverage_module_to_markdown(root: CoverageModule, input_name: str = "coverage.dat") -> str:
    md_lines: list[str] = []

    (
        lines_total,
        lines_hits,
        toggles_total,
        toggles_hits,
        branches_total,
        branches_hits,
        expr_total,
        expr_hits,
    ) = _aggregate(root)

    md_lines.append("# Coverage Report")
    md_lines.append("")
    md_lines.append(f"Generated: {date.today().isoformat()}")
    md_lines.append(f"Input: {input_name}")
    md_lines.append("")
    md_lines.append("## Summary")
    md_lines.append("| Metric | Hit | Total | % |")
    md_lines.append("|--------|-----|-------|---|")
    md_lines.append(f"| Line | {lines_hits} | {lines_total} | {_percent(lines_hits, lines_total)} |")
    md_lines.append(
        f"| Branch | {branches_hits} | {branches_total} | {_percent(branches_hits, branches_total)} |"
    )
    md_lines.append(
        f"| Toggle | {toggles_hits} | {toggles_total} | {_percent(toggles_hits, toggles_total)} |"
    )
    md_lines.append(f"| Expr | {expr_hits} | {expr_total} | {_percent(expr_hits, expr_total)} |")
    md_lines.append("")

    modules = _collect_modules(root)
    md_lines.append("## Modules")
    md_lines.append("| Module | Line % | Branch % | Toggle % | Link |")
    md_lines.append("|--------|--------|----------|----------|------|")
    for module in modules:
        (
            module_lines_total,
            module_lines_hits,
            module_toggles_total,
            module_toggles_hits,
            module_branches_total,
            module_branches_hits,
            _module_expr_total,
            _module_expr_hits,
        ) = _aggregate(module)
        module_id = _anchor_for_module(module)
        md_lines.append(
            f"| {_module_title(module)} | "
            f"{_percent(module_lines_hits, module_lines_total)} | "
            f"{_percent(module_branches_hits, module_branches_total)} | "
            f"{_percent(module_toggles_hits, module_toggles_total)} | "
            f"[details](#{module_id}) |"
        )
    if not modules:
        md_lines.append("| - | - | - | - | - |")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    for module in modules:
        _render_module_sections(module, md_lines)

    md_lines.append("### Tree (hierarchy)")
    if root.children_modules:
        for module in sorted(root.children_modules, key=lambda item: item.hierarchy):
            _render_tree(module, md_lines)
    else:
        md_lines.append("- empty tree")
    md_lines.append("")

    return "\n".join(md_lines)


def write_coverage_markdown(
    root: CoverageModule,
    output_path: str,
    input_name: str = "coverage.dat",
) -> str:
    content = coverage_module_to_markdown(root=root, input_name=input_name)
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(content)
    return output_path
