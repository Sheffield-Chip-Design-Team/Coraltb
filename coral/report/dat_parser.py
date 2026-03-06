from dataclasses import dataclass
from enum import Enum
import re


class CoverageType(str, Enum):
    LINE = "line"
    TOGGLE = "toggle"
    BRANCH = "branch"
    EXPR = "expr"


@dataclass
class DataEntry:
    file: str
    line: int
    column: int
    type: CoverageType
    page: str
    object: str
    hierarchy: str
    hits: int


def _parse_coverage_type(value: str) -> CoverageType:
    return CoverageType(value.strip().lower())

# basically follows verilator dat parser
def dat_parser(dat_file: str) -> list[DataEntry]:
    entries: list[DataEntry] = []

    with open(dat_file, "r", encoding="utf-8", errors="replace") as infile:
        for raw_line in infile:
            line = raw_line.rstrip("\n")
            if not line.startswith("C"): # ignore comments
                continue

            first_quote = line.find("'") # start of a coverage point record (CPR)
            last_quote = line.rfind("'") # end of a CPR

            payload = line[first_quote + 1:last_quote] # content of a CPR
            hits_text = line[last_quote + 1:].strip() # number of hits, its not between quotes

            hits = int(hits_text)

            pairs = re.findall(r"\x01([^\x02]+)\x02([^\x01]*)", payload) # match \x01<key> \x02<value> pairs

            fields = {key.strip(): value.strip() for key, value in pairs} # convert to dict

            file_value = fields.get("f")
            line_value = fields.get("l")
            column_value = fields.get("n")
            type_value = fields.get("t")
            page_value = fields.get("page")
            object_value = fields.get("o")
            hierarchy_value = fields.get("h")


            try:
                entry = DataEntry(
                    file=file_value,
                    line=int(line_value),
                    column=int(column_value),
                    type=_parse_coverage_type(type_value),
                    page=page_value,
                    object=object_value,
                    hierarchy=hierarchy_value,
                    hits=hits,
                )
            except ValueError:
                raise ValueError(f"Invalid line number: {raw_line}")

            entries.append(entry) # add to list

    return entries
