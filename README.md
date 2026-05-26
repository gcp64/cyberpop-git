# Cyberpop AI Git CLI

<div align="center">
  <img src="screenshot.png" alt="Cyberpop AI Git CLI" width="800" style="border-radius: 16px; box-shadow: 0 10px 40px rgba(138, 43, 226, 0.3); margin: 20px 0;" />
</div>

<div align="center">

[![Latest Release](https://img.shields.io/badge/Release-v1.0.0-8a2be2?style=for-the-badge&logo=github)](https://github.com/gcp64/cyberpop-git/releases/tag/v1.0.0)
[![Security Hardened](https://img.shields.io/badge/Security-AES--256--GCM-9b30ff?style=for-the-badge&logo=dependabot)](https://github.com/gcp64/cyberpop-git#security-architecture)
[![AI Engine](https://img.shields.io/badge/AI--Engine-Gemini--2.5-d800ff?style=for-the-badge&logo=google-gemini)](https://github.com/gcp64/cyberpop-git#quick-start--operations-guide)

</div>

---

Cyberpop AI Git CLI is a high-performance, standalone command-line utility designed to automate your Git workflows using advanced language models (Gemini 2.5 Flash and OpenAI). It generates structured Conventional Commits, scans workspaces to build optimized configurations, and compiles daily standup summaries instantly.

Unlike standard CLI helper tools, Cyberpop is built with a local-first, zero-knowledge cryptographic architecture. It ensures complete isolation of your API credentials, preventing credential scraping and key leakage even in hostile developer environments.

Developed by **gcp64** (bob).

---

## Key Benefits

* **Time Efficiency:** Consolidates multiple Git commands (staging, commit message generation, committing, and pushing) into a single, high-speed execution.
* **Standardized Commits:** Automatically generates Conventional Commit messages (e.g., feat, fix, docs, refactor) from staged code diffs to keep repository histories immaculate.
* **Zero-Knowledge Security:** Implements military-grade encryption bound to your local hardware configuration, ensuring API keys cannot be extracted or run on other machines.
* **Instant Reporting:** Generates clean, ready-to-share Markdown Standup Reports based on daily commit activity.
* **Zero Dependencies:** Distributed as a standalone Windows executable (~23 MB) with a cold boot time under 850ms. No Python installation required.

---

## Internal Workflow

When executed, Cyberpop follows a precise, multi-layered sequence to process your commands securely:

1. **Pre-Flight Security Check:** Neutralizes potential local network interception by clearing standard system CA proxy variables and enforcing strict HTTPS certificate validation against official endpoints.
2. **Hardware Key Derivation:** Dynamically reconstructs the local AES decryption key by combining unique system hardware hashes (motherboard MAC address, MachineGuid, active OS username) hashed via SHA-256. 
3. **Workspace Diff Analysis:** Scans the active repository status and extracts staged code differences (`git diff`) securely in memory.
4. **AI Synthesis:** Passes the code diffs securely via TLS to official Gemini/OpenAI servers, instructing the model to generate a strict, highly descriptive Conventional Commit.
5. **Memory Volatile Cleansing:** Mutable key buffers in RAM are overwritten with null bytes (`0x00`) immediately after the network response is received, forcing garbage collection to prevent RAM scraping.
6. **Execution & Push:** Commits the changes using the generated message and executes `git push` to your remote repository branch.

---

## Security Architecture

Cyberpop integrates four distinct layers of active system hardening:

| Security Vector | Implementation Detail |
| :--- | :--- |
| **AES-256-GCM Encryption** | Configuration files are locally encrypted. Keys are bound to system hardware fingerprint (MachineGuid, motherboard MAC, active local username) hashed with SHA-256. Configuration is non-transferable across devices. |
| **RAM Scrape Defense** | Volatile RAM cells are sanitized immediately. API keys are held in mutable `bytearray` buffers and overwritten with `0x00` after execution to prevent memory dump extraction. |
| **MITM Interception Block** | System CA proxy certificate variables (`REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`) are stripped on startup to neutralize network interception. Strict SSL validation is enforced against official endpoints. |
| **Anti-Decompilation** | Compiled and obfuscated using PyArmor to protect core algorithmic assets and prevent binary disassembly. |

---

## Quick Start & Operations Guide

### Step 1: Connect API Key
Configure and encrypt your Gemini API key (default, recommended):
```bash
cyberpop-git config --key YOUR_GEMINI_API_KEY
```
Or configure OpenAI:
```bash
cyberpop-git config --key YOUR_OPENAI_API_KEY --provider openai
```
Verify the active encrypted setup:
```bash
cyberpop-git config --show
```

### Step 2: Initialize Workspace
Scan workspace structure to auto-detect languages/frameworks and generate an optimized `.gitignore` template:
```bash
cyberpop-git init
```

### Step 3: Stage, Commit, and Push
Stage your modifications, generate the AI commit message, and push directly to your repository in one step:
```bash
git add .
cyberpop-git push
```

### Step 4: Generate Standup Report
Summarize today's local commit logs into a clean, markdown-formatted Daily Standup Report:
```bash
cyberpop-git summary
```

---

## Command Reference

| Command | Description |
| :--- | :--- |
| `cyberpop-git config --key <KEY>` | Stores API key with local hardware-bound AES encryption. |
| `cyberpop-git config --show` | Displays active encryption configuration state. |
| `cyberpop-git init` | Detects project structure and writes optimized `.gitignore`. |
| `cyberpop-git push` | Runs diff analysis, commits with Conventional Commit style, and pushes code. |
| `cyberpop-git summary` | Generates a daily work summary in Markdown format. |

---

## Installation from Source

```bash
# Clone the repository
git clone https://github.com/gcp64/cyberpop-git.git
cd cyberpop-git

# Setup environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run CLI
python -m cyberpop_git.main --help
```

---

## License & Terms

* **Attribution:** Developed and copyrighted by **gcp64** (bob). All rights reserved.
* **Privacy:** Local-first execution. Zero telemetry, tracking, or remote database interactions. Direct connections are made exclusively to official AI providers.
* **Disclaimer:** Provided "as-is" without warranty. Users are responsible for confirming code diff analysis complies with internal organizational policies.
