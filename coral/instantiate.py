from coral.parse import *

def parse_files(src_files):
    if not src_files:
        print("No Verilog files found")
        sys.exit(1)

    # Parse all files together
    try:
        ast, _ = parse(src_files, debug=False)
    except Exception as e:
        print(f"Error parsing files: {e}")
        sys.exit(1)

    # Instantiate modules

    declared_signals = set()
    modules = extract_module_info(ast)
    for module_name, ports in modules:
        print("[OUTPUT] Module Instantiation:")
        print(f"  // {module_name}")
        print(generate_instantiation(module_name, ports, declared_signals))
        print(" ")

    cleanup_pyverilog_artifacts()

