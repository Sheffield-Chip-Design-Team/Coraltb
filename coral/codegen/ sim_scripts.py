
import os

def setup_sim_environment (top_module_name="module", simulator="icarus", wtb_name="wtb.v", src_dir="", output_dir=None):
  """Set up the simulation environment by generating necessary files."""

  #  Create output directory if it doesn't exist
  if output_dir and not os.path.exists(output_dir):
      os.makedirs(output_dir)
      print(f"[DEBUG] Created output directory: {output_dir}")
      
  # Generate Makefile
  makefile_content = generate_sim_makefile (top_module_name, simulator, wtb_name, top_module_name, src_dir, output_dir)

  makefile_name = "Makefile.sim"
  with open(makefile_name, "w") as f:
      f.write(makefile_content)
  
  print(f"[DEBUG] Generated simulation Makefile: {makefile_name}")

# Deprecated function - kept for reference
def generate_sim_makefile (top_module_name="", simulator="icarus", wtb_name="wtb.v", src_dir=None, project_sources=[], output_dir=None):
  """Generate a simple Makefile to run the testbench."""

  makefile = []
  use_fst = True

  makefile.append("# Auto-generated Makefile - Coraltb \n")

  makefile.append(f"SIM ?= {simulator} \n")
  makefile.append(f"SRC_DIR ?= {src_dir if src_dir else '.'} \n")

  if use_fst:
    makefile.append(f"FST ?= -fst \n")

  makefile.append("TOPLEVEL_LANG ?= verilog \n")
  makefile.append(f"VERILOG_SOURCES +=")

  for source in project_sources:
      makefile.append(source)
  
  makefile.append(f"SIM_BUILD				= sim_build/rtl")

  # TODO: gate level simulation support 

  makefile.append(f"MODULE = {top_module_name} \n")
  makefile.append("COMPILE_ARGS 		+= -I$(SRC_DIR) \n")
  makefile.append("COCOTB_TEST_MODULES 		+= -I$(SRC_DIR) \n \n")
  # include cocotb's make rules to take care of the simulator setup
  makefile.append("include $(shell cocotb-config --makefiles)/Makefile.sim \n")
    
  return "\n".join(makefile) 





