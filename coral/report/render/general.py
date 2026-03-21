from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from html import escape
from pathlib import Path

from coral.report.models import *

def html_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 24px;
      line-height: 1.4;
    }}
    h1, h2 {{
      margin-bottom: 0.4rem;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin-bottom: 24px;
    }}
    th, td {{
      border: 1px solid #ccc;
      padding: 6px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f5f5f5;
    }}
    .muted {{
      color: #666;
    }}
    .mono {{
      font-family: Consolas, monospace;
    }}
    .section {{
      margin-bottom: 28px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(140px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }}
    .card {{
      border: 1px solid #ccc;
      padding: 12px;
      border-radius: 6px;
      background: #fafafa;
    }}
    .breadcrumbs a {{
      text-decoration: none;
    }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

def pct(hits: int, total: int) -> str:
    if total == 0:
        return "N/A"
    return f"{hits / total * 100:.1f}%"


def module_label(module: CoverageModule) -> str:
    return module.hierarchy if module.hierarchy else module.name or "root"


def module_filename(module: CoverageModule) -> str:
    label = module_label(module)
    safe = (
        label.replace("/", "__")
        .replace("\\", "__")
        .replace(" ", "_")
        .replace("*", "0")
    )
    return f"{safe}.html"

def render_summary(module: CoverageModule) -> str:
    return f"""
<div class="summary">
  <div class="card">
    <strong>Line</strong><br>
    {module.lines_hits}/{module.lines_total} ({pct(module.lines_hits, module.lines_total)})
  </div>
  <div class="card">
    <strong>Toggle</strong><br>
    {module.toggles_hits}/{module.toggles_total} ({pct(module.toggles_hits, module.toggles_total)})
  </div>
  <div class="card">
    <strong>Branch</strong><br>
    {module.branches_hits}/{module.branches_total} ({pct(module.branches_hits, module.branches_total)})
  </div>
  <div class="card">
    <strong>Expr</strong><br>
    {module.expr_hits}/{module.expr_total} ({pct(module.expr_hits, module.expr_total)})
  </div>
</div>
"""

def render_child_modules(module: CoverageModule) -> str:
    if not module.children_modules:
        return "<p class='muted'>No child modules.</p>"

    rows: list[str] = []
    for child in sorted(module.children_modules, key=lambda m: m.hierarchy):
        rows.append(f"""
<tr>
  <td><a href="{escape(module_filename(child))}">{escape(module_label(child))}</a></td>
  <td>{child.lines_hits}/{child.lines_total}</td>
  <td>{child.toggles_hits}/{child.toggles_total}</td>
  <td>{child.branches_hits}/{child.branches_total}</td>
  <td>{child.expr_hits}/{child.expr_total}</td>
</tr>
""")

    return f"""
<table>
  <thead>
    <tr>
      <th>Module</th>
      <th>Line</th>
      <th>Toggle</th>
      <th>Branch</th>
      <th>Expr</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""

def render_points(module: CoverageModule) -> str:
    if not module.children_points:
        return "<p class='muted'>No local points.</p>"

    rows: list[str] = []
    for p in sorted(module.children_points, key=lambda x: (x.file, x.line, x.column, x.type.value)):
        rows.append(f"""
<tr>
  <td class="mono">{escape(p.file)}</td>
  <td>{p.line}</td>
  <td>{p.column}</td>
  <td>{escape(p.type.value)}</td>
  <td class="mono">{escape(p.object)}</td>
  <td>{p.hits}</td>
  <td class="mono">{escape('/'.join(p.page))}</td>
  <td class="mono">{escape('/'.join(p.hierarchy))}</td>
</tr>
""")

    return f"""
<table>
  <thead>
    <tr>
      <th>File</th>
      <th>Line</th>
      <th>Col</th>
      <th>Type</th>
      <th>Object</th>
      <th>Hits</th>
      <th>Page</th>
      <th>Hierarchy</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""

def render_breadcrumbs(module: CoverageModule) -> str:
    chain: list[CoverageModule] = []
    cur = module
    while cur is not None:
        chain.append(cur)
        cur = cur.parent
    chain.reverse()

    parts = [f'<a href="../index.html">root</a>']
    for item in chain:
        parts.append(f'<a href="{escape(module_filename(item))}">{escape(item.name or item.hierarchy)}</a>')

    return f"<div class='breadcrumbs'>{' / '.join(parts)}</div>"

def render_index(root: CoverageModule) -> str:
    rows: list[str] = []
    for child in sorted(root.children_modules, key=lambda m: m.hierarchy):
        rows.append(f"""
<tr>
  <td><a href="modules/{escape(module_filename(child))}">{escape(module_label(child))}</a></td>
  <td>{child.lines_hits}/{child.lines_total}</td>
  <td>{child.toggles_hits}/{child.toggles_total}</td>
  <td>{child.branches_hits}/{child.branches_total}</td>
  <td>{child.expr_hits}/{child.expr_total}</td>
</tr>
""")

    body = f"""
<h1>Coverage Report</h1>

<div class="section">
  <h2>Root Summary</h2>
  {render_summary(root)}
</div>

<div class="section">
  <h2>Top Modules</h2>
  <table>
    <thead>
      <tr>
        <th>Module</th>
        <th>Line</th>
        <th>Toggle</th>
        <th>Branch</th>
        <th>Expr</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</div>
"""
    return html_page("Coverage Report", body)

def render_module_page(module: CoverageModule) -> str:
    title = f"Coverage Module - {module_label(module)}"
    body = f"""
{render_breadcrumbs(module)}
<h1>{escape(module_label(module))}</h1>
<p class="muted">Module report page</p>

<div class="section">
  <h2>Summary</h2>
  {render_summary(module)}
</div>

<div class="section">
  <h2>Child Modules</h2>
  {render_child_modules(module)}
</div>

<div class="section">
  <h2>Local Points</h2>
  {render_points(module)}
</div>
"""
    return html_page(title, body)
