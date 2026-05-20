# 👾 Cyberpop AI Git CLI 👾

<div align="center">
  <img src="icon.png" alt="Cyberpop Logo" width="150" height="150" style="border-radius: 20%;" />
  <p><strong>Local-First • Zero-Knowledge Crypto • High-Performance AI Git Automation</strong></p>
</div>

<div align="center">
  <img src="screenshot.png" alt="Cyberpop App Screenshot" width="800" style="border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.5);" />
</div>

---

**Cyberpop AI Git CLI** is a premium, lightweight, standalone command-line interface (CLI) that automates your Git workflows using state-of-the-art neural networks. Built with a stunning cyberpunk-themed interface, it allows developers to write beautiful, standardized commit messages, initialize project files, and generate daily standup summaries instantly.

Unlike other AI CLI utilities, **Cyberpop** prioritizes your security. It features a robust multi-layered local cryptographic system, preventing API key exposure and credential theft even under hostile environments.

Developed by **gcp64** (bob) with architectural safety and engineering excellence in mind.

---

## 🚀 Key Features

* **`cyberpop-git config`**: Securely configure and save your Gemini or OpenAI API keys, specify model architectures, and define secure proxy variables. All settings are locally encrypted.
* **`cyberpop-git init`**: Scan directory structures dynamically to auto-detect target frameworks and languages, writing a custom, optimized `.gitignore` tailored specifically to your project.
* **`cyberpop-git push`**: Automatically read staged changes (`git diff`), generate Conventional Commit messages using **Gemini 2.5 Flash** (or OpenAI), run the commit protocol, and push to remote branches in one fluid operation.
* **`cyberpop-git summary`**: Synthesize the developer's daily commit history into a beautifully formatted, team-ready markdown **Daily Standup Report**.

---

## 🔒 Zero-Knowledge Cyber Security Hardening

To ensure complete resistance against credential scraping, malicious code injections, and network interception, **Cyberpop** integrates four distinct layers of security:

### 1. Zero-Knowledge Local AES-256 Encryption
API keys are never stored in plaintext inside the configuration files. They are encrypted using **AES-256-GCM** with a dynamic key generated bound to your hardware structure.
* **Hardware Binding**: The key combines the system's Windows registry `MachineGuid`, motherboard MAC address, and active local `username` hashed with SHA-256.
* **Non-Transferability**: If the configuration file is stolen or copied to another machine, decryption attempts fail automatically, returning an empty string.

### 2. Live Volatile Memory Sanitization (RAM Scrape Protection)
Standard string objects in Python persist in RAM until garbage collection runs. Cyberpop counters RAM scraper attacks by:
* Storing keys in mutable `bytearray` objects.
* Wiping key buffers in memory immediately after API calls complete by overwriting the cells with zeroes (`0x00`).
* Forcing `gc.collect()` to clear references and CPU cache lines.

### 3. MITM (Man-in-the-Middle) Proxy Resistance
Upon startup, the CLI strips standard CA proxy certificate environment variables (`REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`). This stops attackers from injecting custom root certificates (e.g., using Fiddler, Charles Proxy) to decrypt the TLS payload sent to the LLM servers. Strict verification is enforced directly via Mozilla's trusted root authority set inside the code.

### 4. Anti-Decompilation & Code Obfuscation
The codebase is compiled and obfuscated using **PyArmor** before building the executable. The binary contains encrypted Python bytecode loaded dynamically with memory-virtualized execution modules, preventing reverse engineering and decompilation back to source code.

---

## 🛠️ Installation & Usage

### Running from Source Code
1. Clone the repository and navigate into the root directory.
2. Initialize virtual environment and install standard requirements:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the CLI modules:
   ```bash
   python -m cyberpop_git.main --help
   ```

### 📦 Building the Standalone `.exe`
A customized build automation script is included to produce a clean, lightweight Windows standalone executable. It automatically excludes over 20 redundant libraries (such as `tkinter`, `unittest`, `multiprocessing`) to keep the binary small (~22 MB).

Run the compilation script:
```bash
python build.py
```
The output executable will be saved directly in `dist/cyberpop-git.exe`.

---

## 🎯 Command Manual

### 1. Setup API Keys
Connect to Gemini API (Default, recommended):
```bash
cyberpop-git config --key YOUR_GEMINI_API_KEY
```
Or use OpenAI models:
```bash
cyberpop-git config --key YOUR_OPENAI_API_KEY --provider openai
```
Show the current encrypted setup:
```bash
cyberpop-git config --show
```

### 2. Intelligent Repository Initialization
Build smart `.gitignore` files based on workspace layout detection:
```bash
cyberpop-git init
```

### 3. Automated Git Commit & Push
Analyze diffs, commit, and push changes to remote:
```bash
cyberpop-git push
```
*Note: If no changes are staged, Cyberpop will ask interactive confirmation to add all files automatically.*

### 4. Standup Report Generator
Synthesize today's commits into a structured leadership report:
```bash
cyberpop-git summary
```

---

## ⚖️ Terms of Use & License

* **Terms of Use**: This application is provided "as-is" without warranty of any kind. You are responsible for ensuring that the code diffs analyzed by the AI providers do not violate your organization's security policies or leak proprietary internal business rules.
* **Privacy Assurance**: The CLI does not communicate with any external backend server owned by third parties except direct REST API calls to the official Gemini/OpenAI endpoints. No telemetry or device metadata is captured.
* **Developer Attribution**: Developed and copyrighted by **gcp64** (bob). All rights reserved.
