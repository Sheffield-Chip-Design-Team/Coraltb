# Written by JAK - v3.0
# Cocotb Environment Test Run Script 

import logging
from rich.logging import RichHandler

import sys
import argparse

from coral import run
from coral.codegen import verilog_wtb
from coral.codegen import python_tb
from coral.common import pyverilog_helpers
from coral.run import sim
import coral.common.config as config

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

    parser.add_argument("--version", "-V", action="version", version="CoralTB v0.3")

    # Create subcommand manager
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Parsing the SIM command
    sim_parser = subparsers.add_parser(
        "sim",
        help="Run a single test, optionally specifying a specific test. [UNIMPLEMENTED]"
    )
    
    sim_parser.add_argument("--test", "-t", type=str, default=1,
                        help="specify the cocotb test to run")
    
    sim_parser.add_argument("--seed", "-s", type=int,
                        help="Force a specific seed")
    
    sim_parser.add_argument("--runs", "-r", type=int, default=1,
                        help="Number of simulation runs")
    
    sim_parser.add_argument("--verbose", "-v", action="count", default=0,
                        help="Set output verbosity level e.g., -v = INFO, -vv - DEBUG")
    
    sim_parser.add_argument("--quiet", "-q", required=False, default=False,
                        action="store_true",
                        help="Run without logging output.")

    
    # Parsing the REGRESS command
    regress_parser = subparsers.add_parser(
        "regress",
        help="Run a test regression of a specific testlist [UNIMPLEMENTED]"
    )
    
    regress_parser.add_argument("--testlist", "-t", type=str, default="sanity",
                        help="specify a testlist file")
    
    regress_parser.add_argument("--iterations", "-i", type=int, default=1,
                        help="Number of times to run the testlist")
    
    regress_parser.add_argument("--verbose", "-v", action="count", default=0,
                        help="Set output verbosity level e.g., -v = INFO, -vv - DEBUG")
        
    regress_parser.add_argument("--quiet", "-q", required=False, default=False,
                        action="store_true",
                        help="Run without logging output.")

    # Parsing the code-gen command
    # -- todo: separate this out into a different file

    code_gen_parser = subparsers.add_parser(
        "code-gen",
        help="Create a verilog or cocotb testbench from RTL sources. [PARTIALLY IMPLEMENTED]"
    )
    
    code_gen_parser.add_argument("--src", "-s", nargs='+', type=str, required=True,
                        help="List of Verilog soruce file(s).")
    
    code_gen_parser.add_argument("--includes", "-I", nargs='+', type=str, required=False,
                        help="List of include files or directories.")

    code_gen_parser.add_argument("--defines", "-D", nargs='+', type=str, required=False,
                        help="List of parameter defines.")
    
    code_gen_parser.add_argument("--verilog-wrap", "-w", required=False, default=True,
                        action="store_true",
                        help="Enable generation of a Verilog testbench wrapper.")
    
    code_gen_parser.add_argument("--cocotb-test", "-c", required=False, default=True,
                        action="store_true",
                        help="Enable generation of a Cocotb heartbeat test template with clock and reset.")

    code_gen_parser.add_argument("--param", "-p", nargs="*", help="Verilog-style +args")

    code_gen_parser.add_argument("--top", "-t", type=str, required=True, help="top module name")

    code_gen_parser.add_argument("--heir", "-H", required=False, default=False,  action="store_true", help="instantiate the module heirarchally")

    code_gen_parser.add_argument("--verbose", "-v", action="count", default=0,
                        help="Set output verbosity level e.g., -v = INFO, -vv - DEBUG")
    
    code_gen_parser.add_argument("--quiet", "-q", required=False, default=False,
                        action="store_true",
                        help="Run without logging output.")
    
    
    # Parsing the CLEAN command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Run a single test, optionally specifying a specific test. [UNIMPLEMENTED]"
    )

    args = parser.parse_args()

    # Setup logger
    quiet = args.quiet if "quiet" in args else False
    setup_logging(args.verbose, quiet)

    logger = logging.getLogger(__name__)

    if args.command == "code-gen":

        logger.debug(f"Parsing modules: {args.src}")
        ast, _ = pyverilog_helpers.parse_design(args.src, args.includes, args.defines)
        
        param_list = []
        param_overrides = []

        if args.param is not None:
            for param in args.param:
                if '=' in param:
                    pname, pvalue = param.split('=')
                    pname = pname.lstrip("+")
                    param_list.append(pname)
                    param_overrides.append(pvalue)

        logger.info(f"Generating basic Verilog testbench for {args.top}")
        verilog_wtb.generate_wtb(ast, args.top , "dut" , param_list , param_overrides, heirarchal=args.heir==True)
        pyverilog_helpers.cleanup_pyverilog_artifacts()

        if args.cocotb_test:
            design_modules = pyverilog_helpers.get_all_modules(ast)
            top_modules = pyverilog_helpers.get_top_modules(design_modules, args.heir==True, args.top)

            for mod in top_modules:
                ports, params = pyverilog_helpers.extract_module_info(mod, param_list, param_overrides)
                test_name = f"test_{mod.name}"
                logger.info(f"Generating cocotb module for: {mod.name}")
                result = python_tb.generate_cocotb_test(mod.name, ports, test_name)
                print(result)

    if args.command == "clean":
        logger.info(f"Cleaning artefacts")
        pyverilog_helpers.cleanup_pyverilog_artifacts()

    if args.command == 'build':
        logger.info("building design...")
        # TODO - implement build functionality

    if args.command == "sim":
        logger.info("running simulation...")
       
        # TODO find the modules that need to be built and ONLY build those (in parallel)

        rtl_sources = []
        rtl_sources.append("/Users/macbook/chip_dev/Coraltb/test/src/ALU.v")
        rtl_sources.append("/Users/macbook/chip_dev/Coraltb/test/sim_test/tb/ArithmeticLogicUnit_wtb.v")
        wtb_name = "arithmeticlogicunit_wtb"

        sim.run_simulation(simulator="icarus", wtb_module=wtb_name, src_dir="", rtl_sources=rtl_sources, test_module=args.test, test_dir=None, output_dir=None)

if __name__ == "__main__":
    main()

