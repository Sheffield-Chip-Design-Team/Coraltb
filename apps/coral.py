# Written by JAK - v3.0
# Cocotb Environment Test Run Script 

import sys
import argparse
from coral import instantiate, verilog

def main():

    parser = argparse.ArgumentParser(
            prog="coral",
            description="SHARC Verification Tool: 'Coraltb' " \
            "Generate Simple Verilog Testbenches for modules." \
            "Generate a scaffold for a cocotb test with a single command." \
            "Run tests and regressions" \
        )
    
    # Create subcommand manager
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Parsing the SIM command
    sim_parser = subparsers.add_parser(
        "sim",
        help="Run a single test, optionally specifying a specific test. [UNIMPLEMENTED]"
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
        help="Run a test regression of a specific testlist [UNIMPLEMENTED]"
    )
    
    regress_parser.add_argument("--testlist", "-t", type=str, default="sanity",
                        help="specify a testlist file")
    
    regress_parser.add_argument("--iterations", "-i", type=int, default=1,
                        help="Number of times to run the testlist")
    
    regress_parser.add_argument("--verbose", "-v",
                        action="store_true",
                        help="Enable verbose output")

    # Parsing the TB-SETUP command
    code_gen_parser = subparsers.add_parser(
        "code-gen",
        help="Create a verilog or cocotb testbench from RTL sources. [PARTIALLY IMPLEMENTED]"
    )
        
    code_gen_parser.add_argument("--verbose", "-v", required=False, default=False,
                        action="store_true",
                        help="Enable verbose output.")
    
    code_gen_parser.add_argument("--src", "-s", nargs='+', type=str, required=True,
                        help="List of Verilog soruce file(s).")
    
    code_gen_parser.add_argument("--includes", "-I", nargs='+', type=str, required=False,
                        help="List of include files or directories.")

    code_gen_parser.add_argument("--defines", "-D", nargs='+', type=str, required=False,
    help="List of parameter defines.")
    
    code_gen_parser.add_argument("--verilog-wrap", "-w", required=False, default=False,
                        action="store_true",
                        help="Enable generation of a Verilog testbench wrapper.")
    
    code_gen_parser.add_argument("--cocotb-test", "-t", required=False, default=True,
                        action="store_true",
                        help="Enable generation of a Cocotb heartbeat test template with clock and reset.")
    
    code_gen_parser.add_argument("--param", "-p", nargs="*", help="Verilog-style +args")


    # Parsing the CLEAN command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Run a single test, optionally specifying a specific test. [UNIMPLEMENTED]"
    )

    args = parser.parse_args()

    print("[DEBUG]", args)

    if args.command == "code-gen":
        ast, directives = verilog.parse_design(args.src, args.includes, args.defines)
        
        param_list = []
        param_overrides = []

        for param in args.param:
            if '=' in param:
                pname, pvalue = param.split('=')
                pname = pname.lstrip("+")
                param_list.append(pname)
                param_overrides.append(pvalue)

        verilog.generate_instantiation(ast, "adder" , "dut", param_list , param_overrides, heirarchal=False)

if __name__ == "__main__":
    main()

