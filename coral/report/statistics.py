from coral.report.models import CoverageModule, CoveragePoint, CoverageType

def _count_point(module: CoverageModule, point: CoveragePoint) -> None:
    if point.type == CoverageType.LINE:
        module.lines_total += 1
        if point.hits > 0:
            module.lines_hits += 1
        return

    if point.type == CoverageType.TOGGLE:
        module.toggles_total += 1
        if point.hits > 0:
            module.toggles_hits += 1
        return

    if point.type == CoverageType.BRANCH:
        module.branches_total += 1
        if point.hits > 0:
            module.branches_hits += 1
        return

    if point.type == CoverageType.EXPR:
        module.expr_total += 1
        if point.hits > 0:
            module.expr_hits += 1


def construct_coverage_hierarchy(points: list[CoveragePoint]) -> CoverageModule: #Build a module tree from CoveragePoint.hierarchy values.
    """
    Notes:
    Root module is synthetic and returned as the tree root.
    Each point is attached only to its exact module (not ancestors).
    """
    root = CoverageModule(name="__root__", hierarchy="")
    modules_by_path: dict[str, CoverageModule] = {"": root}

    for point in points:
        parts = point.hierarchy
        parent = root
        current_path = ""

        for part in parts:
            current_path = f"{current_path}.{part}" if current_path else part
            module = modules_by_path.get(current_path)

            if module is None:
                module = CoverageModule(
                    name=part,
                    hierarchy=current_path,
                    parent=parent,
                )
                parent.children_modules.append(module)
                modules_by_path[current_path] = module

            parent = module

        parent.children_points.append(point)
        _count_point(parent, point)

    return root
