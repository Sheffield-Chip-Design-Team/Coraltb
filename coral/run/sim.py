from logging import info
from pathlib import Path
from cocotb_tools.runner import Runner
import os
import sys

# class Tee:
#     def __init__(self, *streams):
#         self.streams = streams

#     def write(self, data):
#         for s in self.streams:
#             s.write(data)
#             s.flush()

#     def flush(self):
#         for s in self.streams:
#             s.flush()

# orig_execute = Runner._execute

# def tee_execute(self, cmds, cwd):
#     if self.log_file is None:
#         return orig_execute(self, cmds, cwd)

#     with open(self.log_file, "w") as f:
#         tee = Tee(sys.stdout, f)
#         self._execute_cmds(cmds, cwd, tee)

# Runner._execute = tee_execute

from cocotb_tools.runner import get_runner

def run_simulation(simulator="icarus", wtb_top="wtb", src_dir="", rtl_sources=[], test_module="", test_dir=None, waves=True, coverage=False, output_dir=None):
    """Run a cocotb simulation using the specified simulator."""

    sim_build_dir   = (output_dir+"/"+simulator) if output_dir else simulator
    test_output_dir = sim_build_dir+"/"+test_module

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
        
    # if not os.path.isabs(test_module):
    #     if not os.path.isabs(test_module):
    #         test_module_path = os.path.join(test_module_dir, test_module+)
    #         if not os.path.exists(test_module_path):
    #             print(f"[ERROR] Test file {test_module} does not exist.")
    #             return
            
    runner.build(
        verilog_sources=rtl_sources,
        hdl_toplevel=wtb_top,
        build_dir=sim_build_dir,
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
    info(f"Simulation completed: log in {script_run_from}/{test_output_dir}/latest.log")
    