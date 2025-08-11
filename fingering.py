#!/usr/bin/env python3
"""
Gray Fingering - Guarded Multi-threaded Recon Tool
Usage:
  python fingering.py --target example.com --all --auth path/to/authfile [--try-install]

Requirements:
  - subfinder
  - waybackurls
  - httpx
  - nuclei
"""

import os
import sys
import argparse
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from shutil import which
import logging
from colorama import init, Fore, Style
from pyfiglet import Figlet

# Init
init(autoreset=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

REQUIRED_TOOLS = ["subfinder", "waybackurls", "httpx", "nuclei"]
CONFIRM_PHRASE = "I_HAVE_WRITTEN_AUTHORITY"

def banner():
    try:
        f = Figlet(font="bloody")
        print(Fore.RED + Style.BRIGHT + f.renderText("Gray Fingering"))
    except Exception:
        print(Fore.RED + Style.BRIGHT + "=== Gray Fingering ===")
    print(Fore.WHITE + "Guarded Multi-threaded Recon Orchestrator (SAFE by default)\n")

def check_tool(tool):
    return which(tool) is not None

def attempt_install(tool):
    logging.info(f"[installer] Attempting to install: {tool}")
    go_map = {
        "subfinder": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "httpx": "github.com/projectdiscovery/httpx/cmd/httpx@latest",
        "waybackurls": "github.com/tomnomnom/waybackurls@latest",
        "nuclei": "github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest",
    }
    try:
        if tool in go_map and check_tool("go"):
            cmd = f"go install {go_map[tool]}"
            logging.info(f"[installer] Running: {cmd}")
            subprocess.run(cmd, shell=True, check=False)
            return check_tool(tool)
        # Fallback apt-get for basic installs
        logging.info(f"[installer] Trying apt-get install for: {tool}")
        subprocess.run("sudo apt-get update -y", shell=True, check=False)
        subprocess.run(f"sudo apt-get install -y {tool}", shell=True, check=False)
        return check_tool(tool)
    except Exception as e:
        logging.error(f"Failed to install {tool}: {e}")
        return False

def env_guard():
    return os.getenv("GRAY_ALLOWED", "") == "1"

def auth_guard(path):
    return os.path.isfile(path) and os.access(path, os.R_OK)

def ask_confirmation():
    print(Fore.YELLOW + "Type the confirmation phrase to execute real commands:")
    print(Fore.CYAN + f"  {CONFIRM_PHRASE}")
    try:
        ans = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        return False
    return ans == CONFIRM_PHRASE

# Spinner for showing progress
def spinner(task_name, stop_event):
    chars = "|/-\\"
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r[{task_name}] Working... {chars[i % len(chars)]}")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write(f"\r[{task_name}] Done!{' ' * 10}\n")
    sys.stdout.flush()

def run_cmd_capture(cmd, output_file, task_name):
    stop_event = threading.Event()
    thread = threading.Thread(target=spinner, args=(task_name, stop_event))
    thread.start()

    try:
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stop_event.set()
        thread.join()
        if proc.returncode != 0:
            print(f"\n{Fore.RED}[!] {task_name} failed with return code {proc.returncode}")
            print(f"{Fore.RED}[!] stderr:\n{proc.stderr.strip()}")
            return False
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(proc.stdout)
        return True
    except Exception as e:
        stop_event.set()
        thread.join()
        print(f"{Fore.RED}[!] Exception running {task_name}: {e}")
        return False

def safe_write_placeholder(path, cmd):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("[PLACEHOLDER] Command not executed (SAFE mode).\n")
        fh.write("Command that would have run:\n")
        fh.write(cmd + "\n\n")
        fh.write("To execute real commands: set GRAY_ALLOWED=1, pass --auth file, and type the confirmation phrase.\n")

def run_or_placeholder(name, cmd, outpath, execute):
    if execute:
        token = cmd.strip().split()[0]
        if not check_tool(token):
            logging.warning(f"[{name}] Tool '{token}' not found; writing placeholder.")
            safe_write_placeholder(outpath or f"{name}.txt", cmd)
            return False
        return run_cmd_capture(cmd, outpath, name)
    else:
        logging.info(f"[{name}] SAFE mode - writing placeholder")
        safe_write_placeholder(outpath or f"{name}.txt", cmd)
        return False

def pipeline(target, threads, outdir_base, execute, try_installs):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    outdir = os.path.join(outdir_base or os.getcwd(), f"gray_recon_{target}_{ts}")
    os.makedirs(outdir, exist_ok=True)
    logging.info(f"Output directory: {outdir}")

    files = {
        "Subdomains": os.path.join(outdir, "subs.txt"),
        "Wayback": os.path.join(outdir, "wayback.txt"),
        "Live": os.path.join(outdir, "live.txt"),
        "Nuclei": os.path.join(outdir, "nuclei.txt"),
    }

    if execute and try_installs:
        for t in REQUIRED_TOOLS:
            if not check_tool(t):
                logging.warning(f"Tool missing: {t}. Attempting to install.")
                attempt_install(t)

    # Step 1: Subfinder
    cmd_subfinder = f"subfinder -d {target} -silent -all | tee {files['Subdomains']}"
    run_or_placeholder("Subfinder", cmd_subfinder, files["Subdomains"], execute)

    # Step 2: Waybackurls
    cmd_wayback = f"waybackurls {target} > {files['Wayback']}"
    run_or_placeholder("WaybackURLs", cmd_wayback, files["Wayback"], execute)

    # Merge Subdomains + Wayback for HTTPX input
    combined_live = os.path.join(outdir, "combined_live_targets.txt")
    try:
        with open(combined_live, "w", encoding="utf-8") as out_fh:
            if os.path.exists(files["Subdomains"]):
                with open(files["Subdomains"], "r", encoding="utf-8") as fh:
                    for line in fh:
                        out_fh.write(line)
            if os.path.exists(files["Wayback"]):
                with open(files["Wayback"], "r", encoding="utf-8") as fh:
                    for line in fh:
                        out_fh.write(line)
    except Exception as e:
        logging.error(f"Error creating combined live targets file: {e}")
        if not execute:
            #Placeholder file so HTTPX doesn't fail
            safe_write_placeholder(combined_live, "cat subs.txt wayback.txt > combined_live_targets.txt")

    # Step 3: HTTPX
    cmd_httpx = f"httpx -l {combined_live} -silent -status-code -title -follow-redirects | tee {files['Live']}"
    run_or_placeholder("HTTPX", cmd_httpx, files["Live"], execute)

    # Step 4: Nuclei scan on live hosts
    cmd_nuclei = f"nuclei -l {files['Live']} -severity medium,high,critical -o {files['Nuclei']}"
    run_or_placeholder("Nuclei", cmd_nuclei, files["Nuclei"], execute)

    print(Fore.GREEN + Style.BRIGHT + f"\nRecon completed. Results in: {outdir}")
    return outdir

def main():
    parser = argparse.ArgumentParser(description="Gray Fingering - Multi-threaded Recon Orchestrator")
    parser.add_argument("--target", required=True, help="Target domain (authorized only)")
    parser.add_argument("--all", action="store_true", help="Run full")
    parser.add_argument("--threads", type=int, default=4, help="Max parallel threads")
    parser.add_argument("--auth", required=True, help="Path to signed authorization file")
    parser.add_argument("--try-install", action="store_true", help="Try installing missing tools if real execution")
    args = parser.parse_args()

    banner()

    if not args.all:
        logging.error("Use --all to run the full pipeline. Exiting.")
        sys.exit(1)

    if not env_guard():
        logging.warning("Environment variable GRAY_ALLOWED not set. Running in SAFE mode.")

    if not auth_guard(args.auth):
        logging.warning(f"Auth file '{args.auth}' missing.Running in SAFE mode.")

    execute = False
    if env_guard() and auth_guard(args.auth):
        if ask_confirmation():
            logging.info("Confirmation accepted.Execution ENABLED.")
            execute = True
        else:
            logging.warning("Confirmation phrase incorrect. Running in SAFE mode.")

    if not execute:
        os.environ.pop("GRAY_ALLOWED", None)

    pipeline(args.target, args.threads, None, execute, args.try_install)

if __name__ == "__main__":
    main()
