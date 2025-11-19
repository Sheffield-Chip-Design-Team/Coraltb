# Written by JAK - v3.0
# Cocotb Environment Test Run Script 

import sys
import argparse
from coral import instantiate

def show_help():
    """Print Cocotb test runner help and exit."""
    print()
    print("Cocotb Test Runner Script")
    print("James Ashie Kotey - SHaRC 2025")
    print("Usage:")
    print("coral regress --runs or -r <iterations> --width or -w <test_width> [other options]")
    print("coral sim [--tb or -t=<testbench_name>] [other options]")
    print("coral --help or -h")
    print()
    print("Commands:")
    print("  regress   Run regression tests with specified options.")
    print("  sim       Run a simulation, optionally with a testbench.")
    print("  help      Show this help message.")
    sys.exit(0)

def main():

    parser = argparse.ArgumentParser(
            prog="coral",
            description="SHARC RTL Verification Tool: 'Coral' " \
            "Generate Simple Verilog Testbenches for modules." \
            "Generate a scaffold for a cocotb test with a single command." \
            "Run tests and regressions" \
        )
    
    # Create subcommand manager
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Parsing the SIM command
    sim_parser = subparsers.add_parser(
        "sim",
        help="Run a single test, optionally specifying a specific test."
    )
    
    sim_parser.add_argument("--all", "-a", type=int, default=1,
                        help="Number of all tests")
    
    sim_parser.add_argument("--pattern", "-p", type=int, default=1,
                        help="Number of all tests")
    
    sim_parser.add_argument("--tests", "-t", type=int, default=1,
                        help="specify a testname of tests")
    
    sim_parser.add_argument("--runs", "-r", type=int, default=1,
                        help="Number of runs (e.g., different seeds)")

    sim_parser.add_argument("--seed", "-s", type=int,
                        help="Force a specific seed")
    
    sim_parser.add_argument("--verbose", "-v",
                        action="store_true",
                        help="Enable verbose output")


    # Parsing the REGRESS command
    regress_parser = subparsers.add_parser(
        "regress",
        help="Run a test regression of a specific testlist"
    )
    
    regress_parser.add_argument("--testlist", "-t", type=str, default="sanity",
                        help="specify a testlist file")
    
    regress_parser.add_argument("--iterations", "-i", type=int, default=1,
                        help="Number of times to run the testlist")
    
    regress_parser.add_argument("--verbose", "-v",
                        action="store_true",
                        help="Enable verbose output")

    # Parsing the TB-SETUP command
    setup_parser = subparsers.add_parser(
        "code-gen",
        help="Create a verilog or cocotb testbench from RTL sources."
    )
    
    setup_parser.add_argument("--src", "-s", nargs='+', type=str, required=True,
                        help="List of Verilog soruce file(s).")
    
    # Parsing the CLEAN command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Run a single test, optionally specifying a specific test."
    )

    args = parser.parse_args()
    print("[DEBUG]", args)

    if args.command == "code-gen":
        instantiate.parse_files(args.src)


if __name__ == "__main__":
    main()

