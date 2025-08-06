#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpeedO - Terminal Internet Speed & Stress Test Tool
By Dr.Pinnacle (Vishwanath Akuthota © 2025)
"""

import argparse
import time
import os
import sys
import statistics
from datetime import datetime
import threading
import signal

try:
    import speedtest
except ImportError:
    print("Installing speedtest-cli...")
    os.system("pip install speedtest-cli")
    import speedtest

try:
    from ping3 import ping
except ImportError:
    print("Installing ping3...")
    os.system("pip install ping3")
    from ping3 import ping

try:
    from colorama import Fore, Style, init
except ImportError:
    print("Installing colorama...")
    os.system("pip install colorama")
    from colorama import Fore, Style, init

init(autoreset=True)

# ASCII branding
BANNER = r"""
 __                     _   ___ 
/ _\_ __   ___  ___  __| | /___\
\ \| '_ \ / _ \/ _ \/ _` |//  //
_\ \ |_) |  __/  __/ (_| / \_// 
\__/ .__/ \___|\___|\__,_\___/  
   |_|                          
        SpeedO by Dr.Pinnacle (Vishwanath Akuthota ©)
"""

# Stress durations
STRESS_MODES = {
    'L': 300,
    'M': 600,
    'H': 900,
    'V': 1800,
    'E': 3600,
    'D': 86400,
    'Y': 31557600
}

# Handle CTRL+C gracefully
def signal_handler(sig, frame):
    print(Fore.RED + "\nTest aborted by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Speed test logic
def run_speed_test(test_type="ALL", host=None):
    st = speedtest.Speedtest()
    if host:
        st.get_servers([host])
    else:
        st.get_best_server()

    result = {}

    if test_type in ["ALL", "D"]:
        print(Fore.CYAN + "Testing Download Speed...")
        result['download'] = round(st.download() / 1_000_000, 2)  # Mbps
    if test_type in ["ALL", "U"]:
        print(Fore.CYAN + "Testing Upload Speed...")
        result['upload'] = round(st.upload() / 1_000_000, 2)  # Mbps
    if test_type in ["ALL", "P"]:
        print(Fore.CYAN + "Testing Ping & Jitter...")
        pings = [ping(st.best['host'], timeout=2) * 1000 for _ in range(5)]
        valid_pings = [p for p in pings if p is not None]
        result['ping'] = round(min(valid_pings), 2) if valid_pings else None
        result['jitter'] = round(statistics.stdev(valid_pings), 2) if len(valid_pings) > 1 else 0

    return result

# Stress test loop
def stress_test(duration, test_type="ALL", host=None):
    print(Fore.YELLOW + f"Starting stress test for {duration} seconds...")
    end_time = time.time() + duration
    iteration = 1

    while time.time() < end_time:
        print(Fore.GREEN + f"\n--- Iteration {iteration} ---")
        result = run_speed_test(test_type, host)
        print(Fore.MAGENTA + f"Download: {result.get('download', 'N/A')} Mbps | "
                             f"Upload: {result.get('upload', 'N/A')} Mbps | "
                             f"Ping: {result.get('ping', 'N/A')} ms | "
                             f"Jitter: {result.get('jitter', 'N/A')} ms")
        iteration += 1
        time.sleep(2)  # Cooldown between tests

# Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description="SpeedO - Terminal Internet Speed & Stress Test Tool")
    parser.add_argument("-S", "--stress", help="Stress mode (L/M/H/V/E/D/Y) or seconds", default=None)
    parser.add_argument("-T", "--test", help="Specific test: U (upload), D (download), P (ping)", default="ALL")
    parser.add_argument("-r", "--run", type=int, help="Auto-start after delay in seconds", default=0)
    parser.add_argument("-H", "--host", help="Custom host/server", default=None)
    parser.add_argument("-X", "--xhr", type=int, help="Parallel connections (1-32)", default=6)
    parser.add_argument("-P", "--ping", type=int, help="Number of ping samples", default=5)
    parser.add_argument("-O", "--timeout", type=int, help="Ping timeout (ms)", default=5000)
    parser.add_argument("-C", "--clean", type=int, help="Overhead compensation (0-4%)", default=4)
    return parser.parse_args()

def main():
    print(Fore.LIGHTBLUE_EX + BANNER)

    args = parse_args()

    # Auto-start delay
    if args.run > 0:
        print(Fore.YELLOW + f"Starting test in {args.run} seconds...")
        time.sleep(args.run)

    # Determine stress duration
    stress_duration = None
    if args.stress:
        if args.stress.upper() in STRESS_MODES:
            stress_duration = STRESS_MODES[args.stress.upper()]
        else:
            try:
                stress_duration = int(args.stress)
            except ValueError:
                print(Fore.RED + "Invalid stress value. Use L/M/H/V/E/D/Y or seconds.")
                sys.exit(1)

    # Determine test type
    test_map = {"U": "U", "D": "D", "P": "P"}
    test_type = test_map.get(args.test.upper(), "ALL")

    # Run stress test or single test
    if stress_duration:
        stress_test(stress_duration, test_type, args.host)
    else:
        result = run_speed_test(test_type, args.host)
        print(Fore.GREEN + "\n=== Test Result ===")
        print(Fore.CYAN + f"Download: {result.get('download', 'N/A')} Mbps")
        print(Fore.CYAN + f"Upload:   {result.get('upload', 'N/A')} Mbps")
        print(Fore.CYAN + f"Ping:     {result.get('ping', 'N/A')} ms")
        print(Fore.CYAN + f"Jitter:   {result.get('jitter', 'N/A')} ms")

if __name__ == "__main__":
    main()