from dataclasses import dataclass, field
from enum import Enum


class CoverageType(str, Enum):
    LINE = "line"
    TOGGLE = "toggle"
    BRANCH = "branch"
    EXPR = "expr"


@dataclass
class CoveragePoint:
    file: str
    line: int
    column: int
    type: CoverageType
    page: list[str]
    object: str
    hierarchy: list[str]
    hits: int


@dataclass
class CoverageModule:
    name: str = ""
    hierarchy: str = ""
    parent: "CoverageModule | None" = None

    lines_total: int = 0
    lines_hits: int = 0

    toggles_total: int = 0
    toggles_hits: int = 0

    branches_total: int = 0
    branches_hits: int = 0

    expr_total: int = 0
    expr_hits: int = 0

    children_points: list[CoveragePoint] = field(default_factory=list)
    children_modules: list["CoverageModule"] = field(default_factory=list)
