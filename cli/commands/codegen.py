# cli/commands/codegen.py
# CoralTB Code Generation Command

import logging
import coral.common.config as config
from coral.codegen import verilog_wtb
from coral.codegen import python_tb
from coral.common import pyverilog_helpers

logger = logging.getLogger(__name__)

def register(subparsers):
    
    code_gen_parser = subparsers.add_parser(
        "code-gen",
        help="Create a verilog or cocotb testbench from RTL sources. [PARTIALLY IMPLEMENTED]"
    )
    
    code_gen_parser.add_argument("--src", "-s", nargs='+', type=str, required=True,
                        help="List of Verilog soruce file(s).")

    code_gen_parser.add_argument("--output-dir", "-o", type=str, required=False,
                        help="Output directory for generated testbenches.")
    
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
    
    code_gen_parser.set_defaults(func=run_codegen)

def run_codegen(args, logger):
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
    
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = args.top+"_tb"

    verilog_wtb.generate_wtb(ast, args.top , "dut" , param_list , param_overrides, heirarchal=args.heir==True, output_dir=output_dir)
    pyverilog_helpers.cleanup_pyverilog_artifacts()

    if args.cocotb_test:
        design_modules = pyverilog_helpers.get_all_modules(ast)
        top_modules = pyverilog_helpers.get_top_modules(design_modules, args.heir==True, args.top)
    
        for mod in top_modules:
           
            if args.output_dir:
                output_dir = args.output_dir
            else:
                output_dir = mod.name+"_tb"

            ports, params = pyverilog_helpers.extract_module_info(mod, param_list, param_overrides)
            test_name = f"test_{mod.name}"
            logger.info(f"Generating cocotb module for: {mod.name}")
            result = python_tb.generate_cocotb_test(mod.name, ports, test_name, output_dir)
            print(result)


