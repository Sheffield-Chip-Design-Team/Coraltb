# Convenience functions for handling and parsing verilog source files
from pyverilog.vparser.parser import VerilogCodeParser
from pyverilog.vparser.ast import ModuleDef, Paramlist, Decl, Parameter, Localparam, Portlist, Ioport, Identifier, Input, Output, Inout
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

import sys, os 

codegen = ASTCodeGenerator()

# TODO - add config option for keeping parameter definitions in instantiations
# TODO - format the signals nicley (consistent end indentation)

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

#  Module Extraction Functions

def get_all_modules(ast) -> dict:
    """Return a dictionary of all ModuleDef AST nodes in the design."""
    
    modules = {}

    for desc in ast.description.definitions:
        if isinstance(desc, ModuleDef):
            modules[desc.name] = desc
    
    return modules

def get_top_modules(modules, heirarchal, top_modules) -> list:
    """Return a list of top-level ModuleDef AST nodes in the design."""
    module_list = []
    
    for desc in modules.values():
        if not heirarchal:
            if desc.name in top_modules:
                module_list.append(desc)
        else:
            module_list.append(desc)

    return module_list

def extract_module_info(module:ModuleDef, overide_param_names=[], override_param_values=[]):
    """Extract parameter and port information for the specified top module."""
   
    params = create_param_dict(module)
    overriden_params = override_param_dict(create_param_dict(module), overide_param_names, override_param_values)
    ports = create_io_port_dict(get_ports(module), params)

    return ports, overriden_params

# Port Extraction Functions

def get_ports(ast):
    """Return a list of port AST nodes."""
    ports = []
    if isinstance(ast.portlist, Portlist) and ast.portlist.ports:
        for p in ast.portlist.ports:
            # Ports can be Ioport or simple Identifier
            if isinstance(p, Ioport):
                pname = p.first.name  # e.g. 'clk'
                # print(f"[DEBUG] Found io port {pname}")
            elif isinstance(p, Identifier):
                pname = p.name
                # print(f"[DEBUG] Found identifier port {pname}")
            else:
                continue
            ports.append(p)
    return ports
    
def create_io_port_dict(ports, params):
    """Return a dict of port_name -> [port direction, port width]."""
    port_dict = {}
    for p in ports:
        # Ports can be Ioport or simple Identifier
        if isinstance(p, Ioport):
            pname = p.first.name    # e.g. 'clk'
            port_dict[pname] = []
            port_dict[pname].append(get_port_direction(p))
            port_dict[pname].append(get_port_width(p, params))
        elif isinstance(p, Identifier):
            pname = p.name
        else:
            continue

    return port_dict

def get_port_direction(port): 
    """Return the direction of an Ioport ('input', 'output', 'inout')."""
    if isinstance(port, Ioport):
        # print(f"[DEBUG] Getting direction for port {port.first.name}")
        first = port.first
        if isinstance(first, Input):
            return "input"
        elif isinstance(first, Output):
            return "output"
        elif isinstance(first, Inout):
            return "inout"
    return None

def evaluate_width_expr(expr_str) -> int:
    """Evaluate a width expression string and return an integer."""
    try:
        width = eval(expr_str)
        return width
    except Exception as e:
        print(f"[ERROR] Could not evaluate width expression '{expr_str}': {e}")
        return 0
    
def get_port_width(port, params, keep_params=False):
    """
    Return integer (msb value) of a PyVerilog Input/Output/Inout node.
    Returns 1 for scalar (no width declared).
    """
    # TODO find a way to keep the params for manual edits

    w = port.first.width
    if w is None: 
        # scalar wire
        return 0
    else:         
        # vector wire
        print(f"DEBUG: port width for {port.first.name} is {codegen.visit(w)}")
       
        msb = str(codegen.visit(w.msb))
        lsb = str(codegen.visit(w.lsb))
       
        # replace parameters in msb and lsb
        lsb_params = []
        msb_params = []
        
        lsb_elaborated = lsb
        msb_elaborated = msb

        print(params)

        for p in params:
            if p in lsb:
                print(f"DEBUG: replacing lsb param {p} with value {params[p]}")
                lsb_elaborated = lsb.replace(p, str(params[p]))
                lsb_params.append(p)
            if p in msb:
                print(f"DEBUG: replacing lsb param {p} with value {params[p]}")
                msb_elaborated = msb.replace(p, str(params[p]))
                msb_params.append(p)

        print(f"DEBUG: evaluating expression:{lsb_elaborated}")
        print(f"DEBUG: evaluating expression:{msb_elaborated}")

        lsb_evaluated = evaluate_width_expr(lsb_elaborated)
        msb_evaluated = evaluate_width_expr(msb_elaborated)

        print(f"DEBUG: port lsb is {codegen.visit(w.lsb)} evaluated to -> {lsb_evaluated}")
        print(f"DEBUG: port msb is {codegen.visit(w.msb)} evaluated to -> {msb_evaluated}")
        
        if not keep_params:
            width = (msb_evaluated - lsb_evaluated)
        else:
            # reconstruct  simplified width expressions using the input params
            # if parameters were used in msb and lsb, remove it from both sides 
            for p in lsb_params:
                if p in msb_params:
                    print(f"DEBUG: removing common parameter {p} from msb and lsb")
                    lsb_params.remove(p)
                    msb_params.remove(p)
            
            #  construfct lsb expression
        
            #  construct msb expression

            #  put it together
            width = f"({msb} - {lsb})"

        return width

# Parameter Extraction and Override Functions

def create_param_dict(module:ModuleDef) -> dict:
    """Return a dict of parameter_name -> default_value_str."""

    body_params = []
    body_params = get_body_parameters(module)

    header_params = []
    header_params = get_header_parameters(module)

    params = {}
    
    for b in body_params:
        if get_param_type(b) == "parameter":
            name, value = get_body_param_info(b)
            # print(f"[DEBUG] Found parameter {name} with default value {value}")
            params[name] = value

    for h in header_params:
        name, value = get_header_param_info(h)
        # print(f"[DEBUG] Found parameter {name} with default value {value}")
        params[name] = value
    
    return params
        
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

def get_param_type(param):
    """Return 'parameter' or 'localparam'.""" 
    # print(f"[DEBUG] Getting parameter type for {param.name}")
    if isinstance(param, Localparam):
        print(f"[DEBUG] {param.name} is a localparam")
        return "localparam"
    elif isinstance(param, Parameter):
        print(f"[DEBUG] {param.name} is a parameter")
        return "parameter"
    else:
        return None
 
def get_body_param_info(param):
    """Return (name, default_value_str)."""
    name = param.name

    # param.value is an AST node (IntConst, Identifier, BinaryOp, etc.)
    if param.value is None:
        value = None
    else:
        value = str(codegen.visit(param.value))  # <-- converts AST to string

    return name, value

def get_header_param_info(param):
    """Return (name, default_value_str)."""
    name = param.list[0].name

    # param.value is an AST node (IntConst, Identifier, BinaryOp, etc.)
    if param.list[0].value is None:
        value = None
    else:
        value = str(codegen.visit(param.list[0].value))  # <-- converts AST to string

    return name, value

def get_header_parameters(ast):
    """Return a list of header parameter AST nodes."""
    params = [] 
    # header parameters 
    if isinstance(ast.paramlist, Paramlist) and ast.paramlist.params:
        for p in ast.paramlist.params:
            # print(f"[DEBUG] Found header parameter {p.list[0].name}")
            params.append(p)

    return params

def override_param_dict(params, overide_params, param_values) -> dict:
    """Override parameters in the params dict with provided values."""
    if overide_params and param_values:
        for i in range (len(overide_params)):
            # print(f"[DEBUG] Overriding parameter {overide_params[i].upper()} with value {param_values[i]}")
            if overide_params[i].upper() in params or overide_params[i].lower() in params:
                params[overide_params[i].upper()] = param_values[i]
            else :
                print(f"[WARNING] Parameter {overide_params[i]} not found in module, skipping override")
    return params

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