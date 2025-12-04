# Convenience functions for handling and parsing verilog source files
from pyverilog.vparser.parser import VerilogCodeParser
from pyverilog.vparser.ast import ModuleDef, Paramlist, Decl, Parameter, Portlist, Ioport, Identifier, Input, Output, Inout
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

import sys, os , io

codegen = ASTCodeGenerator()

def parse_design (filelist, includes, defines):
    """Parse the verilog design files and return (ast, directives)."""
    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)
        
    if len(filelist) == 0:
        print("No input files specified")
        return None, None
        
    codeparser = VerilogCodeParser(
        filelist,
        preprocess_include=includes,
        preprocess_define=defines
    )
    
    # TODO - figure out how to remove the logging here
    ast = codeparser.parse()
    directives = codeparser.get_directives()

    return ast, directives

def get_ports(ast):
    """Return a list of port AST nodes."""
    ports = []
    if isinstance(ast.portlist, Portlist) and ast.portlist.ports:
        for p in ast.portlist.ports:
            # Ports can be Ioport or simple Identifier
            if isinstance(p, Ioport):
                pname = p.first.name  # e.g. 'clk'
                print(f"[DEBUG] Found io port {pname}")
            elif isinstance(p, Identifier):
                pname = p.name
                print(f"[DEBUG] Found identifier port {pname}")
            else:
                continue
            ports.append(p)
    return ports
    
def create_io_port_dict(ports):
    """Return a dict of port_name -> port direction."""
    port_dict = {}
    for p in ports:
        # Ports can be Ioport or simple Identifier
        if isinstance(p, Ioport):
            pname = p.first.name    # e.g. 'clk'
            port_dict[pname] = get_port_direction(p)
        elif isinstance(p, Identifier):
            pname = p.name
        else:
            continue

    return port_dict

def get_port_direction(port):
    """Return the direction of an Ioport ('input', 'output', 'inout')."""
    if isinstance(port, Ioport):
        print(f"[DEBUG] Getting direction for port {port.first.name}")
        first = port.first
        if isinstance(first, Input):
            return "input"
        elif isinstance(first, Output):
            return "output"
        elif isinstance(first, Inout):
            return "inout"
    return None

def get_body_parameters(ast):
    """Return a list of body parameter AST nodes."""
    params = []

    # body parameters
    for item in ast.items:
        if isinstance(item, Decl):
            for decl in item.list:
                if isinstance(decl, Parameter):
                    params.append(decl)

    return params

def get_body_param_info(param):
    """Return (name, default_value_str)."""
    name = param.name

    # param.value is an AST node (IntConst, Identifier, BinaryOp, etc.)
    if param.value is None:
        value = None
    else:
        value = str(codegen.visit(param.value))  # <-- converts AST to string

    return name, value

def get_header_parameters(ast):
    """Return a list of header parameter AST nodes."""
    params = [] 
    # header parameters 
    if isinstance(ast.paramlist, Paramlist) and ast.paramlist.params:
        for p in ast.paramlist.params:
            params.append(p)

    return params

def generate_instantiation (ast, top_module, inst_name, overide_params=[], param_values=[], heirarchal=False):
    """Generate a verilog instantiation string for a module in the AST."""

    if not heirarchal: # just instantiate the top module
       
        for desc in ast.description.definitions:
            if isinstance(desc, ModuleDef) and desc.name == top_module:
                mod = desc

    top_str = codegen.visit(mod)
    print("[DEBUG] Parsed the top module")
    print(top_str)

    # PARAMETERS 
    param_objects = []
    param_objects = get_body_parameters(mod)
    params = {}
    for p in param_objects:
        name, value = get_body_param_info(p)
        print(f"[DEBUG] Found parameter {name} with default value {value}")
        params[name] = value
    
    # override params
    if overide_params and param_values:
        for i in range (len(overide_params)):
            print(f"[DEBUG] Overriding parameter {overide_params[i].upper()} with value {param_values[i]}")
            if overide_params[i].upper() in params or overide_params[i].lower() in params:
                params[overide_params[i].upper()] = param_values[i]
            else :
                print(f"[WARNING] Parameter {overide_params[i]} not found in module {mod.name}, skipping override")

    # PORTS 
    ports = {}
    ports = create_io_port_dict(get_ports(mod))

    # BUILD STRING
    out = []

    # declare interface signals
    for name, direction in ports.items():
        signal_name = name.upper()
        print(f"[DEBUG] Port {signal_name} is a {direction}")
        if direction == "input":
            out.append(f"reg {signal_name};")
        elif direction == "output": 
            out.append(f"wire {signal_name};")

    out.append("")

    # module name + parameters
    if params:
        out.append(f"{mod.name} #(")
        for i, c in enumerate(params):
            comma = "," if i < len(params) - 1 else ""
            out.append(f"    .{c}({params[c]}) {comma}")
        out.append(f") {inst_name} (")
    else:
        out.append(f"{mod.name} {inst_name} (")
   
    # ports
    for i, c in enumerate(ports):
        comma = "," if i < len(ports) - 1 else ""
        out.append(f"    .{c}({c.upper()}){comma}")

    out.append(");")

    print("[DEBUG] Generated instantiation for the top module \n")

    # TODO write to file instead of printing
    print("\n".join(out))

def cleanup_pyverilog_artifacts():
    for junk in ["parser.out", "parsetab.py", "parsetab.pyc"]:
        try:
            os.remove(junk)
        except FileNotFoundError:
            pass
    pycache = "__pycache__"
    if os.path.isdir(pycache):
        for fn in os.listdir(pycache):
            if fn.startswith("parsetab.") and (fn.endswith(".pyc") or fn.endswith(".pyo")):
                try:
                    os.remove(os.path.join(pycache, fn))
                except FileNotFoundError:
                    pass