# Common Functions for creating and parsing config files 

from pathlib import Path
import yaml
import logging
logger = logging.getLogger(__name__)

def parse_capi2(core_path: Path, target: str = "default") -> list[dict]:
    """
    Parse a CAPI2 .core YAML file and return a flat list of file dicts.

    Each dict contains:
        name            - file path relative to core root (str)
        file_type       - e.g. "systemVerilogSource", "verilogSource" (str)
        is_include_file - True/False (bool)
        logical_name    - VHDL/SV library name, if set (str | None)
        tags            - list of hint strings (list[str])
        fileset         - name of the CAPI2 fileset this file came from (str)
    """
    
    with core_path.open("r", encoding="utf-8") as fh:
        raw = fh.read()

    # CAPI2 files start with "CAPI=2:" which is not valid YAML — strip it
    if raw.startswith("CAPI=2:"):
        raw = raw[len("CAPI=2:"):].lstrip("\n")

    try:
        data = yaml.safe_load(raw)

    except yaml.YAMLError as exc:
        raise ValueError(
            f"Failed to parse {core_path} as YAML.\n"
            f"Detail: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(f"{core_path}: not a valid YAML mapping")
    
    filesets_data: dict = data.get("filesets", {})
    targets_data: dict = data.get("targets", {})

    # Determine which filesets are active for the requested target
    active_filesets: list[str] = []
    if target and target in targets_data:
        tgt = targets_data[target]
        active_filesets = tgt.get("filesets", [])
    else:
        # Fall back: use all filesets if target is unknown / not specified
        active_filesets = list(filesets_data.keys())
        if target:
            logger.warning(
                "Target '%s' not found in %s; using all filesets.", target, core_path
            )

    # Default file_type per fileset (may be overridden per file)
    results: list[dict] = []

    for fs_name in active_filesets:
        # Strip flag expressions like "tool_verilator ? (verilator_tb)"
        fs_name = strip_flag_expression(fs_name)
        if not fs_name:
            continue

        fileset = filesets_data.get(fs_name)
        if fileset is None:
            logger.warning("Fileset '%s' referenced but not defined — skipping.", fs_name)
            continue
        
        default_file_type: str = fileset.get("file_type", "")
        default_logical_name: str | None = fileset.get("logical_name")
        default_tags: list[str] = fileset.get("tags", [])

        core_path = core_path.expanduser().resolve()

        for entry in fileset.get("files", []):
            file_info = parse_file_entry(
                core_path,
                entry,
                default_file_type=default_file_type,
                default_logical_name=default_logical_name,
                default_tags=default_tags,
                fileset_name=fs_name,
            )
            results.append(file_info)
            
    return results

def strip_flag_expression(name: str) -> str:
    """
    CAPI2 fileset references can be conditional expressions such as:
        "tool_verilator ? (verilator_tb)"
    This helper extracts the bare fileset name from the parentheses, or
    returns the name unchanged if there is no such expression.
    Returns an empty string for negated conditions ("!flag ? (name)")
    since we cannot evaluate flags statically.
    """
    name = name.strip()
    if "?" in name:
        # For simplicity: skip negated expressions, include positive ones
        condition, _, rest = name.partition("?")
        condition = condition.strip()
        rest = rest.strip().strip("()")
        if condition.startswith("!"):
            return ""  # Cannot evaluate; skip
        return rest.strip()
    return name

def parse_file_entry(
    core_path: Path,
    entry,
    *,
    default_file_type: str,
    default_logical_name: str | None,
    default_tags: list[str],
    fileset_name: str,
) -> dict:
    """
    Convert a single CAPI2 file entry into a normalised dict.

    CAPI2 allows two forms:
        - A plain string:  "rtl/foo.sv"
        - A mapping:       {"rtl/foo.sv": {file_type: ..., is_include_file: true}}
    """
    if isinstance(entry, str):
        # Plain filename, no per-file overrides
        return {
            "name": entry,
            "file_type": default_file_type,
            "is_include_file": False,
            "logical_name": default_logical_name,
            "tags": list(default_tags),
            "fileset": fileset_name,
        }

    if isinstance(entry, dict):
        # The dict should have exactly one key: the file name
        file_name, attrs = next(iter(entry.items()))
        attrs = attrs or {}
        return {
            "name": file_name,
            "abs_path": core_path.parent / file_name,
            "file_type": attrs.get("file_type", default_file_type),
            "is_include_file": bool(attrs.get("is_include_file", False)),
            "logical_name": attrs.get("logical_name", default_logical_name),
            "tags": list(default_tags) + list(attrs.get("tags", [])),
            "fileset": fileset_name,
        }

    raise ValueError(f"Unexpected file entry type {type(entry)!r}: {entry!r}")

def write_config(file_dicts: list[dict], output_path: Path, core_name: str) -> None:
    from collections import defaultdict

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Group files by file_type; unknown types land under "unknown"
    by_type: dict[str, list[dict]] = defaultdict(list)
    for f in file_dicts:
        key = f.get("file_type") or "unknown"
        by_type[key].append(f)

    lines: list[str] = [
        "# Auto-generated Coral config file.",
        f"# Core : {core_name}",
        f"# Files: {len(file_dicts)}",
        "",
        "[project]",
        f"name: {core_name}",
        f"file_count: {len(file_dicts)}",
        "",
    ]

    for file_type, files in sorted(by_type.items()):
        lines.append(f"[filetype:{file_type}]")
        lines.append(f"count = {len(files)}")
        for idx, f in enumerate(files):
            lines += [
                f"path: {f['abs_path'] if 'abs_path' in f else f['name']}",
                f"include: {'true' if f.get('is_include_file') else 'false'}",
            ]
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %d file entries to %s", len(file_dicts), output_path)
