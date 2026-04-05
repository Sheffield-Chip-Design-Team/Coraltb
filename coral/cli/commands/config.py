# Coral config creation file
import logging
from pathlib import Path

import coral.common.config as config
logger = logging.getLogger(__name__)

# Main CLI entry point
def register(subparsers):
    config_parser = subparsers.add_parser(
        "config",
        help="Parse a CAPI2 .core file and write a file-list config."
    )
     
    config_parser.add_argument("core_file", help="Path to the CAPI2 .core file")
    config_parser.add_argument(
        "--output-file", "-o",
        nargs="?",
        default=None,
        help="Output config file path (default: <core_name>.cfg)",
    )
    config_parser.add_argument(
        "--target", "-t",
        default="default",
        help="CAPI2 target to use (default: 'default')",
    )
   
    config_parser.set_defaults(func=run_config)

def run_config(args, logger):
    core_path = Path(args.core_file)
    core_name = core_path.stem 

    file_dicts = config.parse_capi2(core_path, target=args.target)

    out_path = Path(args.output_file) if args.output_file else Path(f"{core_name}.cfg")
    config.write_config(file_dicts, out_path, core_name)

    print(f"Written {len(file_dicts)} file entries to {out_path}")