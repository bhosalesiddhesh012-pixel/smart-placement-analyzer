#!/usr/bin/env python3
"""
Server Restarter for Smart Placement Analyzer
Kills any existing Flask instance on ports 5001-5005 and starts a fresh instance with auto-reloading.
"""
import os
import sys
import subprocess
import time

def restart_server():
    print("=" * 65)
    print("      RESTARTING SMART CAMPUS PLACEMENT ANALYZER")
    print("=" * 65)
    
    ports = [5001, 5002, 5003, 5004, 5005]
    print(f"Stopping old server instances on ports {ports}...")
    for p in ports:
        try:
            out = subprocess.check_output(f"lsof -t -i:{p}", shell=True).decode().strip()
            if out:
                for pid in out.splitlines():
                    pid = pid.strip()
                    if pid:
                        os.system(f"kill -9 {pid} 2>/dev/null")
                        print(f"  ✓ Stopped process PID {pid} on port {p}")
        except Exception:
            pass

    time.sleep(1)
    print("\nStarting fresh server with live template reload enabled...")
    start_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start.py")
    os.execv(sys.executable, [sys.executable, start_script])

if __name__ == "__main__":
    restart_server()
