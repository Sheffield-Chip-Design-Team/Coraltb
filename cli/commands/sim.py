
# cli/commands/sim.py
# CoralTB Simulation Command

from logging import info
import os
from pathlib import Path
import sys

import coral.common.config as config
import coral.run.sim as sim

def register(subparsers):
    
    sim_parser = subparsers.add_parser(
        "sim",
        help="Run a single test, optionally specifying a specific test. [UNIMPLEMENTED]"
    )

    sim_parser.add_argument("--config", "-c", type=str, required=False, default=1,
                        help="specify the test config file ton use")
    
    sim_parser.add_argument("-dut", "-d", type=str, default="",
                    help="specify the name of the dut wtb module.")
    
    sim_parser.add_argument("--test-module", "-t", type=str, default=1,
                        help="specify the cocotb test module to run")
    
    sim_parser.add_argument("--output-dir", "-o", type=str, default="",
                    help="specify the output directory for the test module")

    sim_parser.add_argument("--seed", "-s", type=int,
                        help="Force a specific seed")
    
    sim_parser.add_argument("--runs", "-r", type=int, default=1,
                        help="Number of simulation runs")
    
    sim_parser.add_argument("--waves", "-w", default=False,
                        action="store_true",
                        help="Switch for enabling or disabling waveform generation")
    
    sim_parser.add_argument("--cov", "-u", default=False,
                        action="store_true",
                        help="Switch for enabling or disabling coverage reportiing")

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
    info(f"Searching for source directories in {current_dir}")
    for root, dirs, files in os.walk(current_dir):
        for dir_name in dirs:
            if 'src' in dir_name.lower() or 'rtl' in dir_name.lower():
                src_dir = Path(root) / dir_name
                src_dirs.append(src_dir)
             
    info(f"Searching for wtb files in directory in {current_dir}")
    for root, dirs, files in os.walk(current_dir):
        for dir_name in dirs:
            if 'tb' in dir_name.lower():
                test_dir = Path(root) / dir_name
                src_dirs.append(test_dir)
              

    # Remove duplicates while preserving order
    src_dirs = list(set(src_dirs))
    info(f"Found source directories: {src_dirs}")

    # Collect all .v files from found src directories
    v_files = []
    for src_dir in src_dirs:
        for v_file in src_dir.rglob('*.v'):
            # Get relative path from the src directory
            rel_path = v_file.relative_to(current_dir)
            info(f"Discovered Verilog file: {rel_path}")
            v_files.append(str(rel_path))

    return v_files, str(current_dir)
def discover_test_module(test_module):
    """Locate cocotb test module and make it importable."""
    current_dir = Path.cwd()
    test_file = None

    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file == f"{test_module}.py":
                test_file = Path(root) / file
                break

    if test_file is None:
        raise FileNotFoundError(
            f"Could not find cocotb test module '{test_module}.py'"
        )

    test_dir = test_file.parent

    info(f"Discovered test module at: {test_file}")
    info(f"Adding to PYTHONPATH: {test_dir}")

    sys.path.insert(0, str(test_dir))

        
def compile_sources(sources):
    # Placeholder for compilation logic
    pass

def run_sim(args, logger):
    discover_test_module(args.test_module) 
       
    logger.info(f"Running Test: {args.test_module}")
    
    src_files, src_root_dir = discover_sources()
    print(f"Discovered source files: {src_files} in dir {src_root_dir}")
    
    wtb_name = args.dut
    output_dir = args.output_dir if args.output_dir else "sim"

    
    sim.run_simulation(simulator="icarus", 
        wtb_top=wtb_name, 
        src_dir=src_root_dir,
        rtl_sources=src_files, 
        test_module=args.test_module, 
        output_dir=args.output_dir,
        waves=bool(args.waves),
        coverage=bool(args.cov)
    )
   
    # rtl_sources = []
    # rtl_sources.append("/Users/macbook/chip_dev/Coraltb/test/src/ALU.v")
    # rtl_sources.append("/Users/macbook/chip_dev/Coraltb/test/sim_test/tb/ArithmeticLogicUnit_wtb.v")
   


