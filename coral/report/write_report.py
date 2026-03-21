from pathlib import Path

from coral.report.models import CoverageModule
from coral.report.render.general import module_filename, render_index, render_module_page

def write_report(root: CoverageModule, out_dir: Path) -> None:
    modules_dir = out_dir / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "index.html").write_text(render_index(root), encoding="utf-8")

    def walk(module: CoverageModule) -> None:
        (modules_dir / module_filename(module)).write_text(
            render_module_page(module),
            encoding="utf-8",
        )
        for child in module.children_modules:
            walk(child)

    for child in root.children_modules:
        walk(child)