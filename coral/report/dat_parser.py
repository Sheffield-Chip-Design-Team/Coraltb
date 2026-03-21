import re
from coral.report.models import CoveragePoint, CoverageType


def _parse_coverage_type(value: str) -> CoverageType:
    return CoverageType(value.strip().lower())


def _split_page(value: str) -> list[str]:
    return [part for part in value.strip().split("/") if part]


def _split_hierarchy(value: str) -> list[str]:
    parts: list[str] = []
    for segment in value.strip().split("/"):
        if not segment:
            continue
        parts.extend(part for part in segment.split(".") if part)
    return parts


# basically follows verilator dat parser
def dat_parser(dat_file: str) -> list[CoveragePoint]:
    points: list[CoveragePoint] = []

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
                point = CoveragePoint(
                    file=file_value,
                    line=int(line_value),
                    column=int(column_value),
                    type=_parse_coverage_type(type_value),
                    page=_split_page(page_value),
                    object=object_value,
                    hierarchy=_split_hierarchy(hierarchy_value),
                    hits=hits,
                )
            except ValueError:
                raise ValueError(f"Invalid line number: {raw_line}")

            points.append(point) # add to list

    return points
