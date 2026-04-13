
# cli/commands/sim.py
# CoralTB Synthesis Command

from logging import info
import os
from pathlib import Path


import coral.common.config as cfg
import coral.synth.synthesis as synth

def register(subparsers):
    
    synth_parser = subparsers.add_parser(
        "synth",
        help="Run a single test module in a cocotb simulation environment."
    )

    synth_parser.add_argument("--output-dir", "-o", type=str, default=None,
                    help="specify the output directory for the synthesis outputs.")

    synth_parser.add_argument("--svg",  default=True,
                        action="store_true",
                        help="Force a specific seed random seed for a test.")

    synth_parser.add_argument("--config", "-c", type=str, default=None,
                        help="specify the edam config file to use for the simulation.")
    
    synth_parser.add_argument("--verbose", "-v", action="count", default=1,
                        help="Set output verbosity level e.g., -v = Verbose/Debug Output.")
    

    synth_parser.set_defaults(func=run_synth)

def run_synth(args, logger):
    if not args.config:
       logger.error("No config file specified. Please provide an edam config file using the --config option.")
       return
    else:
        logger.info(f"Config file specified: {args.config}, loading configuration.")
        config = cfg.load_edam_to_config(args.config)
        
        src_root_dir = "."
        src_files = config.verilog_sources
      
        logger.info(f"Running Synthesis for : {args.test_module}")
        logger.info(f"Using config file: {args.config}")

    output_dir = args.output_dir if args.output_dir else "synth"
    
    # TODO add logic for sv2v and yosys stuff
    #
    


