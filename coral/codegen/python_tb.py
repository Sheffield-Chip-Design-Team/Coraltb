#!/usr/bin/env python3
import argparse
import logging

from random import randint
from jinja2 import Template
from coral.common.pyverilog_helpers import *

logger = logging.getLogger(__name__)

#  TODO use jinja2 templates for test generation

#  TODO decide if I should randomize the reset signal or not
#  TODO add value constraint overrides to the port dictionary

def generate_cocotb_test(module_name, ports, test_name, output_dir="tb") -> str:
    
    clk_signal  = find_port(ports, ["clk", "clock"])
    rst_signal  = find_port(ports, ["rst", "reset"])

    sanity_name = test_name.removeprefix("test_")
    test_file   = f"{output_dir}/{test_name.lower()}.py"
    template    = ""

    if not clk_signal:

        logger.info(f"generating combinational sanity test for {module_name}: (clock not found)")

        input_ports = {}
        input_ports, _ , _ = filter_ports_by_direction(ports)
        clk_port = find_port(ports, ["clk", "clock"])

        # exclude the clock input port from randomization
        if clk_port in input_ports:
            logger.debug(f"Excluding clock port {clk_port} from input randomization.")
            input_ports = input_ports.pop(clk_port)
        
        template = f"""import cocotb
from random import randint
from cocotb.triggers import Timer

async def test_{sanity_name}_combinational(uut):
  # set random input values
"""
        for name, info in input_ports.items():

            max_value = max(2**evaluate_width_expr(str(info['width']))-1,1)
            template += f'  uut.{name}.value = randint(0,{max_value})\n'
            template += f'  uut._log.info("Setting {name} to {{uut.{name}.value}}")\n\n'
            
        template += f"""  await Timer(randint(1,10), unit="ns")
  
  # TODO - add checks for expected output values

  uut._log.info("Test Complete!")""" 

    elif rst_signal:

        logger.info(f"clock and reset found in {module_name}: {clk_signal}, {rst_signal}")

        # Check if reset signal is active-low (ends with '_n')
        active_low_reset = rst_signal.lower().endswith('_n')
        if (active_low_reset):
            start_rst = 0
            end_rst = 1
        else:
            start_rst = 1
            end_rst = 0

        template = f"""import cocotb
from random import randint
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
import os

async def reset(uut, reset_duration=randint(1,10)):
    # assert reset
    uut._log.info("Resetting Module")
    uut.{rst_signal}.value = {start_rst}
    await ClockCycles(uut.{clk_signal}, reset_duration)
    uut.{rst_signal}.value = {end_rst}

@cocotb.test()
async def test_{sanity_name}_sanity(uut):
    # start clock
    clock = Clock(uut.{clk_signal}, 40, units="ns")
    cocotb.start_soon(clock.start())
    await ClockCycles(uut.{clk_signal}, 1)

    # reset the module
    await reset(uut)
    await RisingEdge(uut.{clk_signal})

    # continue test ...
    await ClockCycles(uut.{clk_signal}, 100)
    uut._log.info("Test Complete!")

    """

    else:
        logger.info(f"generating clock-only sanity test for {module_name}: (reset not found)")
        template = f""
        
    os.makedirs(output_dir, exist_ok=True)
    
    with open(test_file, "w") as f:
        f.write(template)
    
    logger.info(f"Generated cocotb test template {test_file}.")
    return f"Generated cocotb test template: {test_file}"


if __name__ == "__main__":
    # Example usage
    cleanup_pyverilog_artifacts()