# Written by JAK - v3.0
# Cocotb Environment Test Run Script 

import logging
from rich.logging import RichHandler

import sys
import argparse

import importlib
import pkgutil

from coral import run
from coral.run import sim
import coral.common.config as config
import cli.commands as commands_module

def setup_logging(verbosity, quiet=False):
    if not quiet:
        if verbosity == 0:
            level = logging.WARNING
        elif verbosity == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG
    else:
        level = logging.ERROR

    logging.basicConfig(
        level=level,
        format="[%(name)s] %(message)s",
        handlers=[RichHandler(rich_tracebacks=True, markup=False)]
    )

def main():
    parser = argparse.ArgumentParser(
        prog="coral",
        description="SHARC Verification Tool: 'Coraltb' "    \
        "Generate Simple Verilog Testbenches for modules."   \
        "Generate basic cocotb tests with a single command." \
        "Run tests and regressions" \
    )   
     
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,  # Python 3.7+
    )

    # Dynamically discover command modules
    for module_info in pkgutil.iter_modules(commands_module.__path__):
        module_name = f"cli.commands.{module_info.name}"
        module = importlib.import_module(module_name)

        # convention: module exposes register(subparsers)
        if hasattr(module, "register"):
            module.register(subparsers)

    args = parser.parse_args()

    # Setup logger
    quiet = args.quiet if "quiet" in args else False
    setup_logging(args.verbose, quiet)
    logger = logging.getLogger(__name__)
    args.func(args, logger)

if __name__ == "__main__":
    main()

