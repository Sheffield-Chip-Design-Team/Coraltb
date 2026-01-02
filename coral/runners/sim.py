from pathlib import Path
from cocotb_tools.runner import get_runner
import os

def run_simulation(simulator="icarus", wtb_module="test_top", src_dir="", rtl_sources=[], top_module="", test_dir=None, output_dir=None):
    """Run a cocotb simulation using the specified simulator."""

    # Enable waveform dumping
    os.environ["WAVES"] = "1"

    python_test_dir = test_dir if test_dir else os.getcwd()
    sim_build_dir   = (output_dir+"/"+simulator) if output_dir else simulator

    runner = get_runner("icarus")

    for source in rtl_sources:
        if not os.path.isabs(source):
            source = os.path.join(src_dir, source)
        if not os.path.exists(source):
            print(f"[ERROR] Source file {source} does not exist.")
            return

    runner.build(
        verilog_sources=rtl_sources,
        hdl_toplevel=wtb_module,
        build_dir=sim_build_dir,
    )

    runner.test(
        hdl_toplevel=wtb_module,
        test_module=top_module,
        test_dir=python_test_dir,
    )
