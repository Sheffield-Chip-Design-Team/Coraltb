# Coverage Report

Generated: 2026-03-18
Input: coverage.dat

## Summary
| Metric | Hit | Total | % |
|--------|-----|-------|---|
| Line | 1 | 1 | 100.0% |
| Branch | 2 | 2 | 100.0% |
| Toggle | 20 | 26 | 76.9% |
| Expr | 2 | 2 | 100.0% |

## Modules
| Module | Line % | Branch % | Toggle % | Link |
|--------|--------|----------|----------|------|
| top | 100.0% | 100.0% | 76.9% | [details](#module-top) |
| top.sub | N/A | N/A | 80.0% | [details](#module-top-sub) |

---

## Module: top {#module-top}

### Local summary
| Metric | Hit | Total | % |
|--------|-----|-------|---|
| Line | 1 | 1 | 100.0% |
| Branch | 2 | 2 | 100.0% |
| Toggle | 12 | 16 | 75.0% |
| Expr | 2 | 2 | 100.0% |

### Toggle
| File | Line | Object | Count | Status |
|------|------|--------|-------|--------|
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 2 | clk:0->1 | 30 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 2 | clk:1->0 | 29 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 3 | rst:0->1 | 2 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 3 | rst:1->0 | 2 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 4 | counter[0]:0->1 | 10 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 4 | counter[0]:1->0 | 10 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 4 | counter[1]:0->1 | 6 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 4 | counter[1]:1->0 | 5 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 4 | counter[2]:0->1 | 2 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 4 | counter[2]:1->0 | 2 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 4 | counter[3]:0->1 | 2 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 4 | counter[3]:1->0 | 1 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 5 | result1:0->1 | 0 | Not reach |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 5 | result1:1->0 | 0 | Not reach |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 6 | result2:0->1 | 0 | Not reach |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 6 | result2:1->0 | 0 | Not reach |

### Branch
| File | Line | Kind | Count |
|------|------|------|-------|
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 21 | if | 20 |
| /home/verilog_env/works/cocotb-verilator/rtl/top.v | 21 | else | 10 |

## Module: top.sub {#module-top-sub}

### Local summary
| Metric | Hit | Total | % |
|--------|-----|-------|---|
| Line | 0 | 0 | N/A |
| Branch | 0 | 0 | N/A |
| Toggle | 8 | 10 | 80.0% |
| Expr | 0 | 0 | N/A |

### Toggle
| File | Line | Object | Count | Status |
|------|------|--------|-------|--------|
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 2 | counter[0]:0->1 | 20 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 2 | counter[0]:1->0 | 20 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 2 | counter[1]:0->1 | 12 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 2 | counter[1]:1->0 | 10 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 2 | counter[2]:0->1 | 4 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 2 | counter[2]:1->0 | 4 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 2 | counter[3]:0->1 | 4 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 2 | counter[3]:1->0 | 2 | OK |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 3 | result:0->1 | 0 | Not reach |
| /home/verilog_env/works/cocotb-verilator/rtl/sub.v | 3 | result:1->0 | 0 | Not reach |

### Branch
| File | Line | Kind | Count |
|------|------|------|-------|
| - | - | - | - |

### Tree (hierarchy)
<details>
  <summary>top (line 100.0%, branch 100.0%, toggle 76.9%)</summary>

  <details>
    <summary>top.sub (line N/A, branch N/A, toggle 80.0%)</summary>

    - local points: 10
  </details>
  - local points: 21
</details>
