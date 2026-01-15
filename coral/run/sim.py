from pathlib import Path
from cocotb_tools.runner import get_runner
import os

def run_simulation(simulator="icarus", wtb_module="test_top", src_dir="", rtl_sources=[], test_module="", test_dir=None, output_dir=None):
    """Run a cocotb simulation using the specified simulator."""

    sim_build_dir   = (output_dir+"/"+simulator) if output_dir else simulator

    if not test_dir:    
        test_module_dir = "/Users/macbook/chip_dev/Coraltb/test/sim_test/tb" # TODO - make this dynamic

    # Enable waveform dumping
    os.environ["WAVES"] = "1"
    
    runner = get_runner(simulator)

    for source in rtl_sources:
        if not os.path.isabs(source):
            source = os.path.join(src_dir, source)
        if not os.path.exists(source):
            print(f"[ERROR] Source file {source} does not exist.")
            return
        
    # if not os.path.isabs(test_module):
    #     if not os.path.isabs(test_module):
    #         test_module_path = os.path.join(test_module_dir, test_module+)
    #         if not os.path.exists(test_module_path):
    #             print(f"[ERROR] Test file {test_module} does not exist.")
    #             return
            
    runner.build(
        verilog_sources=rtl_sources,
        hdl_toplevel=wtb_module,
        build_dir=sim_build_dir,
    )

    runner.test(
        waves=True,
        log_file=f"{sim_build_dir}/latest.log",
        hdl_toplevel=wtb_module,
        test_module=test_module,
        test_dir=test_module_dir
    )
    


