import subprocess
import os
import argparse
from datetime import datetime
import concurrent.futures
from tqdm import tqdm

def run_test(runs=1, width=5):
    # find all directories with a test Makefile inside
    folders_with_makefile = []
    for root, _, files in os.walk("."):
        if "Makefile" in files or "makefile" in files:
            folders_with_makefile.append(root)
    if '.' in folders_with_makefile:
        folders_with_makefile.remove('.')
    print(f"Test directories: {folders_with_makefile}")

    def run_make(folder, run_idx, position):
        module_name = os.path.basename(os.path.abspath(folder))
        desc = f"{module_name} run {run_idx}"
        log_header = f"\n=== {desc} ===\n"

        # Start a separate progress bar for this task
        with tqdm(total=1, desc=desc, position=position, leave=True) as pbar:
            result = subprocess.run(
                ["make"],
                cwd=folder,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            pbar.update(1)

        return log_header + result.stdout

    # Create a flat list of all tasks
    tasks = []
    for folder in folders_with_makefile:
        for run_idx in range(1, runs + 1):
            tasks.append((folder, run_idx))
    print(f"Total tasks: {len(tasks)}")
    print(f"Running {min(width, len(tasks))} batches at a time.")

    logs = [None] * len(tasks)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(width, len(tasks))) as executor:
        future_to_idx = {}
        for idx, (folder, run_idx) in enumerate(tasks):
            position = idx % width  # position for tqdm to avoid overlapping bars
            future = executor.submit(run_make, folder, run_idx, position)
            future_to_idx[future] = idx

        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            logs[idx] = future.result()

    # Write all logs to the master log file in order
    master_log_filename = "latest_regress.log"
    with open(master_log_filename, "a") as master_log:
        master_log.write(f"=== Regression Log ===\n")
        master_log.write(f"Timestamp: {datetime.now().isoformat()}\n")
        master_log.write(f"Test directories: {folders_with_makefile}\n")
        master_log.write(f"Repetitions per directory: {runs}\n")
        master_log.write(f"Threads used: {min(width, len(tasks))}\n")
        master_log.write(f"Total tasks: {len(tasks)}\n")
        master_log.write(f"========================\n\n")
        
        for log in logs:
            master_log.write(log)

def main():
    parser = argparse.ArgumentParser(description="Run make in folders with Makefile.")
    parser.add_argument("-runs", type=int, default=1, help="Number of repetitions per folder")
    parser.add_argument("-width", type=int, default=4, help="Number of threads to use")
    args = parser.parse_args()
    run_test(runs=args.runs, width=args.width)

if __name__ == "__main__":
    main()

