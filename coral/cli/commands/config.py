# Coral config creation file
import logging
from pathlib import Path

import coral.common.config as config
logger = logging.getLogger(__name__)

def register(subparsers):
    config_parser = subparsers.add_parser(
        "config",
        help="Parse a CAPI2 .core file and write a file-list config."
    )
    config_parser.add_argument("top_core", help="Name of the core (e.g. rp_rv32i_sc_wb")

    config_parser.add_argument(
        "--target", "-t",
        default="default",
        help="Name of simulation target (e.g. tb_top)",
    )
    config_parser.add_argument(
        "--output-file", "-o",
        nargs="?",
        default=None,
        help="Output config file path (default: <core_name>.cfg)",
    )

    config_parser.set_defaults(func=run_config)

def run_config(args, logger):
    edam = config.fusesoc_setup(args)
