#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpeedO v2 - Internet Speed & Stress Test ToolBy Dr.Pinnacle (Vishwanath Akuthota © 2025)
"""

import argparse
import time
import os
import sys
import statistics
import json
import subprocess
from datetime import datetime
import signal
import csv

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

# Prepare logs folder & file
def init_log_file():
    os.makedirs("logs", exist_ok=True)
    filename = datetime.now().strftime("logs/speedo_%Y-%m-%d_%H-%M-%S.csv")
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "download_mbps", "upload_mbps", "ping_ms", "jitter_ms"])
    return filename

def log_to_csv(filename, result):
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            result.get("download", "N/A"),
            result.get("upload", "N/A"),
            result.get("ping", "N/A"),
            result.get("jitter", "N/A")
        ])

# Run speedtest-cli via subprocess
def run_speedtest_cli():
    try:
        result = subprocess.run(
            ["speedtest-cli", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(Fore.RED + "Error running speedtest-cli:")
            print(result.stderr)
            return None

        data = json.loads(result.stdout)
        return {
            "download": round(data["download"] / 1_000_000, 2),
            "upload": round(data["upload"] / 1_000_000, 2),
            "ping": round(data["ping"], 2)
        }

    except FileNotFoundError:
        print(Fore.RED + "speedtest-cli not installed. Install with:")
        print(Fore.YELLOW + "  pip install speedtest-cli")
        sys.exit(1)

# Calculate jitter using ping3
def calculate_jitter(host, samples=5, timeout=5000):
    pings = []
    for _ in range(samples):
        res = ping(host, timeout=timeout/1000)  # ms to sec
        if res:
            pings.append(res * 1000)
        time.sleep(0.2)
    if len(pings) > 1:
        return round(statistics.stdev(pings), 2)
    return 0

# ASCII bar renderer
def render_ascii_bar(label, value, max_value, width=20):
    if value == "N/A" or max_value == 0:
        bar = "-" * width
    else:
        filled = int((value / max_value) * width)
        filled = min(filled, width)
        bar = "█" * filled + "-" * (width - filled)
    return f"{label:<9} |{bar}| {value} Mbps"

# Combined test (Download, Upload, Ping, Jitter)
def run_speed_test(test_type="ALL", ping_samples=5, timeout=5000):
    result = {}

    # Run speedtest-cli for download/upload/ping
    if test_type in ["ALL", "D", "U", "P"]:
        cli_result = run_speedtest_cli()
        if not cli_result:
            return result

        if test_type in ["ALL", "D"]:
            result["download"] = cli_result["download"]
        if test_type in ["ALL", "U"]:
            result["upload"] = cli_result["upload"]
        if test_type in ["ALL", "P"]:
            result["ping"] = cli_result["ping"]

    # Add jitter calculation (pinging google.com as fallback)
    if test_type in ["ALL", "P"]:
        jitter = calculate_jitter("8.8.8.8", samples=ping_samples, timeout=timeout)
        result["jitter"] = jitter

    return result

# Stress test loop with live ASCII + logging
def stress_test(duration, test_type="ALL", ping_samples=5, timeout=5000):
    print(Fore.YELLOW + f"Starting stress test for {duration} seconds...")
    end_time = time.time() + duration
    iteration = 1

    # Track stats for summary
    downloads, uploads, pings, jitters = [], [], [], []

    # Init CSV log
    log_file = init_log_file()

    while time.time() < end_time:
        result = run_speed_test(test_type, ping_samples, timeout)

        # Track results
        if "download" in result: downloads.append(result["download"])
        if "upload" in result: uploads.append(result["upload"])
        if "ping" in result: pings.append(result["ping"])
        if "jitter" in result: jitters.append(result["jitter"])

        # Log to CSV
        log_to_csv(log_file, result)

        # Determine scaling (max observed so far for bars)
        max_dl = max(downloads) if downloads else 100
        max_ul = max(uploads) if uploads else 100

        # Render ASCII bars
        sys.stdout.write("\033c")  # Clear terminal
        print(Fore.LIGHTBLUE_EX + BANNER)
        print(Fore.GREEN + f"--- Iteration {iteration} --- ({datetime.now().strftime('%H:%M:%S')})\n")
        print(Fore.CYAN + render_ascii_bar("Download", result.get("download", 0), max_dl))
        print(Fore.CYAN + render_ascii_bar("Upload", result.get("upload", 0), max_ul))
        print(Fore.CYAN + f"Ping: {result.get('ping', 'N/A')} ms | Jitter: {result.get('jitter', 'N/A')} ms")

        iteration += 1
        time.sleep(2)  # Cooldown

    # Summary
    print(Fore.YELLOW + "\n=== Stress Test Summary ===")
    if downloads:
        print(f"Download: avg {statistics.mean(downloads):.2f} Mbps, min {min(downloads)} Mbps, max {max(downloads)} Mbps")
    if uploads:
        print(f"Upload:   avg {statistics.mean(uploads):.2f} Mbps, min {min(uploads)} Mbps, max {max(uploads)} Mbps")
    if pings:
        print(f"Ping:     avg {statistics.mean(pings):.2f} ms, min {min(pings)} ms, max {max(pings)} ms")
    if jitters:
        print(f"Jitter:   avg {statistics.mean(jitters):.2f} ms, min {min(jitters)} ms, max {max(jitters)} ms")

    print(Fore.MAGENTA + f"\nResults logged to: {log_file}")

# Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description="SpeedO v2 - Internet Speed & Stress Test Tool")
    parser.add_argument("-S", "--stress", help="Stress mode (L/M/H/V/E/D/Y) or seconds", default=None)
    parser.add_argument("-T", "--test", help="Specific test: U (upload), D (download), P (ping)", default="ALL")
    parser.add_argument("-r", "--run", type=int, help="Auto-start after delay in seconds", default=0)
    parser.add_argument("-P", "--ping", type=int, help="Number of ping samples", default=5)
    parser.add_argument("-O", "--timeout", type=int, help="Ping timeout (ms)", default=5000)
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
        stress_test(stress_duration, test_type, args.ping, args.timeout)
    else:
        result = run_speed_test(test_type, args.ping, args.timeout)
        print(Fore.GREEN + "\n=== Test Result ===")
        print(Fore.CYAN + f"Download: {result.get('download', 'N/A')} Mbps")
        print(Fore.CYAN + f"Upload:   {result.get('upload', 'N/A')} Mbps")
        print(Fore.CYAN + f"Ping:     {result.get('ping', 'N/A')} ms")
        print(Fore.CYAN + f"Jitter:   {result.get('jitter', 'N/A')} ms")

if __name__ == "__main__":
    main()
