# import sys
# import subprocess

# # TODO - Function to Checking Sv2v and Yosys are installed and available in the system PATH


# # CoralTB Synthesis Flow
# # TODO - translate this into python function s usnig subprocess to call sv2v and yosys

# sv2v "$RTL_FILE" > "$BUILD_DIR/up_down_counter.v"

# yosys -p "read_verilog $BUILD_DIR/up_down_counter.v; prep -top $DUT_TOP; write_json $BUILD_DIR/up_down_counter.json"

# netlistsvg "$BUILD_DIR/up_down_counter.json" -o "$BUILD_DIR/up_down_counter.svg"

# print() "Flow complete. Outputs:"
# echo "  - $BUILD_DIR/up_down_counter.v"
# echo "  - $BUILD_DIR/up_down_counter.json"
# echo "  - $BUILD_DIR/up_down_counter.svg"
