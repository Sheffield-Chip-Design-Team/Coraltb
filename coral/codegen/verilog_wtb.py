import argparse
from coral.common.pyverilog_helpers import *

# Code Generation Functions

logger = logging.getLogger(__name__)

# TODO - format the signals niceley (consistent end indentation)

def instantiate_module(module_name, inst_name, ports, params) -> str:
    """Generate a verilog instantiation string for a module."""
    
    # BUILD STRING
    out = []
    out.append(" ")

    # declare interface signals
    out.append(f"module {module_name.lower()}_wtb;")  # blank line
    out.append(f"\n  // {module_name} instantation signals")

    # net type
    for name, info in ports.items():
        decl_str = "  "
        signal_name = name.upper()
        # print(f"[DEBUG] Port {signal_name} is a {info[0]}")

        #  direction
        if (info['direction'] == "input"):
            decl_str += (f"reg  ")
        else:
            #  outputs, inout or none
                decl_str += (f"wire ")

        # net width 
        if info['width'] != 0: 
            decl_str += (f"[{str(info['width'])}:0]")

        decl_str += (f" {signal_name};")
        out.append(decl_str)
    
    out.append("")  # blank line

    # module name + parameters
    if params:
        out.append(f"  {module_name} #(")
        for i, c in enumerate(params):
            comma = "," if i < len(params) - 1 else ""
            out.append(f"      .{c}({params[c]}){comma}")
        out.append(f"  ) {inst_name} (")
    else:
        out.append(f"{module_name} {inst_name} (")

    # ports
    for i, c in enumerate(ports):
        comma = "," if i < len(ports) - 1 else ""
        out.append(f"      .{c}({c.upper()}){comma}")

    out.append("  );")
    out.append(f"\nendmodule \n")  
    output_str = "\n".join(out)


    logger.debug("Generated instantiation! \n")
    logger.debug(f"{output_str}")

    return output_str
    
def generate_wtb(ast, top_module, inst_name, overide_params=[], param_values=[], heirarchal=False, keep_params=False, output_dir="tb"):
    """Generate a verilog wtb for module(s) in the AST."""

    design_modules = get_all_modules(ast)
    top_modules = get_top_modules(design_modules, heirarchal, top_module)

    if (len(top_modules) == 0):
        if heirarchal:
            logger.error(f"No modules found in design")
        else:   
            logger.warning(f"[WARNING] Top module {top_module} not found in design")
        return
    
    for mod in top_modules:
        
        ports, params = extract_module_info(mod, overide_params, param_values)        
        
        # FOR DEBUGGING 
        logger.debug(f"Parsed module {mod.name}")

        # top_str = codegen.visit(mod)
        # print(top_str)

        out = ""
        out = instantiate_module(mod.name, inst_name, ports, params)
        
        os.makedirs(output_dir, exist_ok=True)

        with open(f"{output_dir}/{mod.name}_wtb.v", "w") as f:
          f.write("// Auto-generated Verilog Testbench Wrapper - Coraltb \n")
          f.write(out)
          f.write(" ")

        logger.info(f"WTB written to {mod.name}_wtb.v!")

# TODO - example main function to parse arguments and call appropriate functions

def main():
    parser = argparse.ArgumentParser(
        description="CoralTB - A Cocotb-based Testbench Generation and Management Tool"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Parsing the CODE-GEN command
    code_gen_parser = subparsers.add_parser(
        "code-gen",
        help="Generate a Verilog testbench wrapper for a specified module."
    )

if __name__ == '__main__':
    main()