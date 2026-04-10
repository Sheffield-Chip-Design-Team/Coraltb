
# cli/commands/sim.py
# CoralTB Simulation Command

from logging import info
import os
from pathlib import Path
import sys
import subprocess

import coral.common.config as cfg
import coral.run.sim as sim

def register(subparsers):
    
    sim_parser = subparsers.add_parser(
        "sim",
        help="Run a single test module in a cocotb simulation environment."
    )

    sim_parser.add_argument("--dut", "-d", type=str, default="",
                    help="specify the name of the dut wtb module.")
    
    sim_parser.add_argument("--test-module", "-t", type=str, default="",
                        help="specify the cocotb test module to run")

    sim_parser.add_argument("--exe", "-x", type=str, default="icarus",
                        help="specify the simulator to run the test in (e.g., icarus, verilator, etc.)")
    
    sim_parser.add_argument("--output-dir", "-o", type=str, default=None,
                    help="specify the output directory for the test module (optional)")

    sim_parser.add_argument("--seed", "-s", type=int, default=None,
                        help="Force a specific seed random seed for a test.")
    
    sim_parser.add_argument("--runs", "-r", type=int, default=1,
                        help="Number of simulation repeats [UNIMPLEMENTED]")
    
    sim_parser.add_argument("--waves", "-w", default=False,
                        action="store_true",
                        help="Switch for enabling or disabling waveform generation")
    
    sim_parser.add_argument("--cov", "-u", default=False,
                        action="store_true",
                        help="Switch for enabling or disabling coverage reporting [PARTIAL SUPPORT]")
    
    sim_parser.add_argument("--config", "-c", type=str, default=None,
                        help="specify the edam config file to use for the simulation (optional)")
    
    sim_parser.add_argument("--verbose", "-v", action="count", default=1,
                        help="Set output verbosity level e.g., -v = Verbose/Debug Output")
    
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

    current_dir = Path.cwd()

    v_files = [
        str(f.relative_to(current_dir))
        for f in current_dir.rglob("*.v")
        if f.name != "cocotb_iverilog_dump.v"
    ]

    for f in v_files:
        info(f"Discovered Verilog file: {f}")

    return sorted(v_files), str(current_dir)
    return v_files, str(current_dir)

def discover_test_module(test_module, local_mode=True):
    """Locate cocotb test module and make it importable."""
    if local_mode:
        current_dir = Path.cwd()
        test_file = None

        for root, dirs, files in os.walk(current_dir):
            for file in files:
                if file == f"{test_module}.py":
                    test_file = Path(root) / file
                    break
    else:
        test_file = Path(test_module).resolve()

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
    if not args.config:
        logger.info(f"Running Test: {args.test_module}")
        src_files, src_root_dir = discover_sources()
        print(f"Discovered source files: {src_files} in dir {src_root_dir}")
    
        logger.info("No config file specified, automatically searching for sources and running simulation.")
                        
        dut_name = args.dut
        if not dut_name.endswith("_wtb"):
            wtb_name = dut_name +"_wtb"
        else:
            dut_name.removesuffix("_wtb")
            wtb_name = dut_name

        test_name = args.test_module
        if not test_name:
            test_name = "test_"+dut_name
            discover_test_module(test_name) 
    else:
        logger.info(f"Config file specified: {args.config}, loading configuration.")
        config = cfg.load_edam_to_config(args.config)
        for test in config.test_files:
            discover_test_module(test, False)
        
        src_root_dir = "."
        src_files = config.verilog_sources
        wtb_name = config.toplevel
        test_name = config.test_module
        
        logger.info(f"Running Test: {args.test_module} with DUT: {wtb_name} using simulator: {args.exe}")
        logger.info(f"Config test files: {src_files}")
        logger.info(f"Config top-level WTB: {wtb_name}")
        logger.info(f"Config test module: {test_name}")

    output_dir = args.output_dir if args.output_dir else "sim"
    
    sim.run_simulation(
        seed=args.seed,
        quiet=args.quiet,
        verbosity=args.verbose,
        simulator=args.exe, 
        wtb_top=wtb_name, 
        src_dir=src_root_dir,
        rtl_sources=src_files, 
        test_module=test_name, 
        output_dir=args.output_dir,
        waves=bool(args.waves),
        coverage=bool(args.cov)
    )

    # cleanup and generate coverage report if necessary
    build_path = output_dir+"verilator/build/results/"

    if bool(args.cov):
        logger.info(f"Collecting coverage information from {build_path}")
        subprocess.run(["verilator_coverage", "--annotate", build_path+"coverage", build_path+"coverage.dat"])
        subprocess.run(["verilator_coverage", "--write-info", build_path+"coverage/coverage.info", build_path+"coverage.dat"])
        subprocess.run(["genhtml", build_path+"coverage/coverage.info", "--output-directory", build_path+"coverage/html"])
        logger.info(f"Coverage report generated at {build_path}coverage/html")


