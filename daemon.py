import subprocess
import time
from datetime import datetime

def run_cycle():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} --- STARTING TRADING CYCLE ---")

    scripts = ['scanner.py', 'strategy.py', 'trader.py']

    for script in scripts:
        print(f"Executing {script}...")
        result = subprocess.run(['py', '-3.11', script], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"SUCCESS: {script} completed.")
            print(result.stdout)
        else:
            print(f"ERROR: {script} failed with return code {result.returncode}.")
            print(result.stderr)
            print("--- HALTING TRADING CYCLE ---")
            return # Halt the cycle on first error

    print(f"{timestamp} --- CYCLE COMPLETE ---")

if __name__ == '__main__':
    run_cycle()
