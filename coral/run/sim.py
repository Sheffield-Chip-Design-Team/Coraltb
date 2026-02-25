from logging import info
from pathlib import Path
from cocotb_tools.runner import Runner
import os
import sys

from cocotb_tools.runner import get_runner

def run_simulation(simulator="icarus", wtb_top="wtb", src_dir="", rtl_sources=[], test_module="", test_dir=None, waves=True, coverage=False, output_dir=None):
    """Run a cocotb simulation using the specified simulator."""

    sim_build_dir = (output_dir+"/"+simulator+"/build") if output_dir else simulator
    test_output_dir = sim_build_dir+"/"+"results"
  
    build_path = Path(sim_build_dir)

    os.environ["COCOTB_LOG_LEVEL"] = "INFO"      # or DEBUG

    if waves:
        # Enable waveform dumping
        os.environ["WAVES"] = "1"

    if coverage:
        # Enable coverage collection
        os.environ["COCOTB_USER_COVERAGE"] = "1"
    
    runner = get_runner(simulator)

    for source in rtl_sources:
        if not os.path.isabs(source):
            source = os.path.join(src_dir, source)
        if not os.path.exists(source):
            print(f"[ERROR] Source file {source} does not exist.")
            return
    
    import shutil
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
   
    build_args = []
    if simulator == "verilator":
        build_args = ['--Wno-TIMESCALEMOD']

    runner.build(
        clean=True,
        verilog_sources=rtl_sources,
        hdl_toplevel=wtb_top,
        build_dir=sim_build_dir,
        build_args = build_args
    )

    runner.test(
        timescale=("1ns", "1ps"),
        waves=waves,
        log_file=f"{test_output_dir}/latest.log",
        hdl_toplevel=wtb_top,
        test_module=test_module,
        test_dir=test_output_dir
    )
    
    script_run_from = os.getcwd()

    # Display the output log
    logfile_path = f"{script_run_from}/{test_output_dir}/latest.log"
    with open(logfile_path, "r") as f:
        for line in f:
            print(line, end="") 

    info(f"Simulation completed: see log in {logfile_path}")

    
