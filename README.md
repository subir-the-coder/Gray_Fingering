# Gray_Fingering
Gray Fingering — Guarded Multi-threaded Recon Orchestrator with nuclei JSON parsing. Automates recon with built-in safeguards, highlights critical findings, and generates detailed HTML reports. Ideal for authorized bug bounty hunters &amp; pentesters.

# Gray Fingering

**Guarded Multi-threaded Recon Orchestrator with Nuclei JSON Parsing**

---

## Overview

Gray Fingering is a powerful and secure multi-threaded reconnaissance automation tool designed for authorized security testing and bug bounty hunting. It integrates industry-leading tools like **subfinder**, **httpx**, **waybackurls**, **katana**, **gau**, **nuclei**, and more — orchestrated in a safe-by-default manner to avoid accidental misuse.

The tool generates detailed HTML reports that highlight **High** and **Critical** findings from nuclei scans, helping security professionals quickly identify and prioritize vulnerabilities.

---

## Features

- Multi-threaded orchestration for fast, efficient recon.
- Safe mode by default to prevent accidental real scans without authorization.
- Strong execution guards requiring environment variable, auth file, and typed confirmation.
- Integration with multiple reconnaissance tools:
  - Subdomain discovery (`subfinder`)
  - Live host detection (`httpx`)
  - URL crawling (`katana`, `waybackurls`, `gau`)
  - Parameter discovery (`paramspider`)
  - XSS detection (`kxss`, `dalfox`)
  - Directory brute forcing (`ffuf`)
  - Vulnerability scanning (`nuclei`) with JSON parsing and report generation.
- Automatic generation of passive OSINT links (GitHub dorks, Shodan, Censys).
- Generates a detailed HTML report highlighting critical vulnerabilities in color.
- Attempts best-effort installation of missing tools (optional).

---

## Installation

Gray Fingering relies on several external tools. You can install them manually or let the script attempt automatic installation (requires Go and apt).

Required tools include:

- [subfinder](https://github.com/projectdiscovery/subfinder)
- [httpx](https://github.com/projectdiscovery/httpx)
- [waybackurls](https://github.com/tomnomnom/waybackurls)
- [katana](https://github.com/projectdiscovery/katana)
- [gau](https://github.com/lc/gau)
- [paramspider](https://github.com/devanshbatham/ParamSpider)
- [kxss](https://github.com/Emoe/kxss)
- [dalfox](https://github.com/hahwul/dalfox)
- [ffuf](https://github.com/ffuf/ffuf)
- [nuclei](https://github.com/projectdiscovery/nuclei)

---

## Usage

1. **Prepare authorization:**

   - Set the environment variable `GRAY_ALLOWED=1`
   - Create an authorization file (can be an empty file, but must exist)
   - Run the script with the `--auth` argument pointing to this file.
   - Type the confirmation phrase when prompted.

2. **Run the full pipeline:**

   ```bash
   export GRAY_ALLOWED=1
   touch auth.txt
   python fingering.py --target example.com --all --auth auth.txt --try-install


View the report:

After the run completes, an HTML report will be generated in the output directory. Open it in your browser to review findin

## Example

python fingering.py --target simplia.com --all --auth auth.txt --try-install

Important Notes
Authorized Testing Only: Use Gray Fingering only on domains you have explicit permission to test.

The script is SAFE by default and will only run real commands if all guards are passed.

The confirmation phrase for execution is: I_HAVE_WRITTEN_AUTHORITY

Make sure all required tools are installed or allow the script to attempt installing them.

Requires Python 3.8+ and the colorama, pyfiglet libraries (pip install colorama pyfiglet).

License
MIT License — feel free to use and modify for your authorized security projects.

Contact
Created by Subir Sutradhar (Gray Code)

<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/67e59b17-b9e8-49af-947d-8dce9d5f2c52" />


Contributions
Contributions, issues, and feature requests are welcome!

Please fork the repository and submit pull requests.

Happy Hunting!

