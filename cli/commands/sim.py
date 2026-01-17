
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

    sim_parser.add_argument("--config", "-c", type=str, required=False, default=1,
                        help="specify the test config file ton use")
    
    sim_parser.add_argument("--test-module", "-m", type=str, default=1,
                        help="specify the cocotb test module to run")
    
    sim_parser.add_argument("--test-dir", "-d", type=str, default="",
                    help="specify the test directory for the test module")
    
    sim_parser.add_argument("--output-dir", "-o", type=str, default="",
                    help="specify the output directory for the test module")

    sim_parser.add_argument("--seed", "-s", type=int,
                        help="Force a specific seed")
    
    sim_parser.add_argument("--runs", "-r", type=int, default=1,
                        help="Number of simulation runs")
    
    sim_parser.add_argument("--waves", "-w", type=int, default=1,
                        help="Switch for enabling or disabling waveform generation")
    
    sim_parser.add_argument("--cov", "-u", type=int, default=1,
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
    
    return v_files, src_dirs[0]

def compile_sources(sources):
    # Placeholder for compilation logic
    pass

def run_sim(args, logger):
    logger.debug(f"Running Test: {args.test_module}")
    
    src_files, src_root_dir = discover_sources()
    print(f"Discovered source files: {src_files}")
   
    wtb_name = args.test_module

    output_dir = args.output_dir if args.output_dir else "sim"

    sim.run_simulation(simulator="icarus", 
        wtb_module=wtb_name, 
        src_dir=src_root_dir,
        rtl_sources=src_files, 
        wtb_module=wtb_name,
        test_module=args.test_module, 
        test_dir=args.test_dir, 
        output_dir=args.output_dir,
        waves=bool(args.waves),
        coverage=bool(args.cov)
    )
   
   
   
    # rtl_sources = []
    # rtl_sources.append("/Users/macbook/chip_dev/Coraltb/test/src/ALU.v")
    # rtl_sources.append("/Users/macbook/chip_dev/Coraltb/test/sim_test/tb/ArithmeticLogicUnit_wtb.v")
   


