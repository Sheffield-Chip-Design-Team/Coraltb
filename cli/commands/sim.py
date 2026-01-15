
# cli/commands/sim.py
# CoralTB Simulation Command

import os
from pathlib import Path

import coral.common.config as config
import coral.run.sim as sim

def register(subparsers):
    
    sim_parser = subparsers.add_parser(
        "sim",
        help="Run a single test, optionally specifying a specific test. [UNIMPLEMENTED]"
    )

    sim_parser.add_argument("--test", "-t", type=str, default=1,
                        help="specify the cocotb test to run")
    
    sim_parser.add_argument("--filelist", "-f", type=str, default=1,
                        help="specify the list of source files used in the simulation.")
    
    sim_parser.add_argument("--seed", "-s", type=int,
                        help="Force a specific seed")
    
    sim_parser.add_argument("--runs", "-r", type=int, default=1,
                        help="Number of simulation runs")
    
    sim_parser.add_argument("--verbose", "-v", action="count", default=0,
                        help="Set output verbosity level e.g., -v = INFO, -vv - DEBUG")
    
    sim_parser.add_argument("--quiet", "-q", required=False, default=False,
                        action="store_true",
                        help="Run without logging output.")
    
    sim_parser.set_defaults(func=run_sim)

def discover_sources():
    # Find directories named 'src' or 'SRC' recursively
    src_dirs = []
    current_dir = Path.cwd()
    
    for root, dirs, files in os.walk(current_dir):
        for dir_name in dirs:
            if 'src' in dir_name.lower():
                src_dirs.append(Path(root) / dir_name)
    
    # Collect all .v files from found src directories
    v_files = []
    for src_dir in src_dirs:
        for v_file in src_dir.rglob('*.v'):
            # Get relative path from the src directory
            rel_path = v_file.relative_to(src_dir)
            v_files.append(str(rel_path))
    
    return v_files
    return []

def compile_sources(sources):
    # Placeholder for compilation logic
    pass

def run_sim(args, logger):
    logger.debug(f"Running Test: {args.test}")
    
    # TODO find the modules that need to be built and ONLY build those (in parallel)
    src_files = discover_sources()
    print(f"Discovered source files: {src_files}")

    # rtl_sources = []
    # rtl_sources.append("/Users/macbook/chip_dev/Coraltb/test/src/ALU.v")
    # rtl_sources.append("/Users/macbook/chip_dev/Coraltb/test/sim_test/tb/ArithmeticLogicUnit_wtb.v")
   
    # wtb_name = "arithmeticlogicunit_wtb"

    # sim.run_simulation(simulator="icarus", wtb_module=wtb_name, src_dir="", rtl_sources=rtl_sources, test_module=args.test, test_dir=None, output_dir=None)

