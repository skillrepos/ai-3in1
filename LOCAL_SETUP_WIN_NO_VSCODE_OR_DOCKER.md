# Local Setup for Windows (No Codespace / No Docker / No Dev Container)
 
### NOTE: GitHub Codespaces — as detailed in the README.md file — are the preferred and recommended environment for these labs. Use this guide only if you can't use a Codespace and can't run the Dev Container locally either.
 
This guide sets up everything the labs need directly on your Windows machine — no Docker, no Dev Containers extension. You'll install Python, Ollama, Git, and a couple of small CLI tools, then run the labs from a regular terminal.
 
<br>
**Instructions below use PowerShell.** Open PowerShell from the Start menu (regular, not Admin, is fine unless an installer asks for it).
 
---
 
## 1. Install Git
 
Download and install from [git-scm.com](https://git-scm.com). Accept the defaults during install.
 
Verify it worked:
```powershell
git --version
```
 
<br>
## 2. Install Python 3.11
 
Download the Python 3.11 installer from [python.org/downloads](https://www.python.org/downloads/). (3.10–3.12 will also work; the workshop's Docker image is built on Python 3.11.)
 
**Important:** On the first installer screen, check the box **"Add python.exe to PATH"** before clicking Install.
 
Verify it worked in a **new** PowerShell window:
```powershell
python --version
pip --version
```
 
<br>
## 3. Install jq
 
One lab step uses `jq` to pretty-print JSON from a `curl` call. Easiest options:
 
- If you have `winget`: `winget install jqlang.jq`
- Or download `jq-windows-amd64.exe` from the [jq releases page](https://github.com/jqlang/jq/releases), rename it to `jq.exe`, and place it somewhere on your PATH (e.g., `C:\Windows`).
Verify:
```powershell
jq --version
```
 
<br>
## 4. Install Ollama
 
Download the Windows installer from [ollama.com/download](https://ollama.com/download) and run it.
 
Ollama installs itself as a background service/tray app and will normally already be listening on `http://localhost:11434` once installed — you usually do **not** need to manually run `ollama serve`. Verify it's up:
```powershell
ollama --version
ollama list
```
If `ollama list` fails to connect, start it manually:
```powershell
ollama serve
```
(Leave that window open/running, and open a **new** PowerShell window for everything else.)
 
<br>
## 5. (Optional but recommended) Install VS Code
 
The labs use a "diff and merge" technique (`code -d file1 file2`) to build out code side-by-side. This works in a normal local install of VS Code — you do **not** need the Dev Containers extension or Docker for it.
 
Download from [code.visualstudio.com](https://code.visualstudio.com/download) and install. During install, make sure **"Add to PATH"** is checked so the `code` command works from PowerShell.
 
Verify:
```powershell
code --version
```
 
If you'd like the hover "thought bubble" comments that appear during the merge steps (shown in the labs.md screenshots), you can install the extension manually once you've cloned the repo (step 7 below):
```powershell
code --install-extension .\.devcontainer\merge-info-0.1.0.vsix
```
This is cosmetic only — the merges themselves work fine without it.
 
<br>
## 6. Clone the repository
 
```powershell
git clone https://github.com/skillrepos/ai-3in1
cd ai-3in1
```
 
<br>
## 7. Create a Python virtual environment and install dependencies
 
The workshop's Docker image installs CPU-only PyTorch *before* the rest of `requirements.txt` to keep things small and avoid pulling in GPU packages. Do the same locally:
 
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```
 
> If PowerShell blocks the activation script with an execution-policy error, run this once and try again: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
 
Each time you open a new terminal to work on the labs, re-activate the environment:
```powershell
cd ai-3in1
.venv\Scripts\Activate.ps1
```
 
<br>
## 8. Pull the model and warm everything up
 
```powershell
ollama pull llama3.2
python warmup_models.py
```
 
This mirrors Lab 1's steps 4 and 12 and pre-loads the LLM and embedding model so the rest of the labs start quickly.
 
<br>
## 9. You're ready — follow labs.md
 
Open `labs.md` in VS Code (or your browser) and start at **Lab 1**. A few small adaptations for Windows/PowerShell as you go:
 
- Wherever the lab says `ollama serve &`, on Windows just run `ollama serve` in its own window (no `&`), or skip it entirely if Ollama is already running as a background service.
- Setting an environment variable for one command (e.g. `OLLAMA_KEEP_ALIVE=-1 ollama serve &`) is written PowerShell-style as:
```powershell
  $env:OLLAMA_KEEP_ALIVE="-1"; ollama serve
```
- The `curl ... | jq -r '.response'` command in Lab 1, step 7 works as written as long as `jq` is on your PATH (step 3 above). If you get a PowerShell alias conflict with `curl`, use `curl.exe` instead of `curl`.
- Steps that say `code -d file1 file2` or `code file.py` work the same as in the Codespace, as long as VS Code is installed and on PATH (step 5).
- Anywhere the lab references starting a second terminal (Lab 3, Lab 5), just open a second PowerShell window/tab, `cd` into the `ai-3in1` folder, and re-activate the virtual environment (`.venv\Scripts\Activate.ps1`) before running commands there.
Everything else in `labs.md` — the Python scripts, the MCP server, ChromaDB, the agents — runs identically to the Codespace once your environment is active and Ollama is running.
 
<br>
## Troubleshooting
 
- **`ollama` or `python` not recognized:** close and reopen PowerShell after installing (PATH changes need a fresh shell), or double-check "Add to PATH" was checked during install.
- **Port 11434 already in use:** Ollama is likely already running as a background service — you don't need to start it again.
- **`pip install` fails on `torch`:** make sure you ran the CPU-only `torch` install command in step 7 *before* `pip install -r requirements.txt`.
- **Antivirus/firewall prompts for Ollama:** allow it — the labs call `http://localhost:11434` and `http://127.0.0.1:8000` only (local traffic).
---
 
## License and Use
 
These materials are provided as part of the virtual training conducted by **TechUpSkills (Brent Laster)**.
 
Use of this repository is permitted **only for registered workshop participants** for their own personal learning and
practice. Redistribution, republication, or reuse of any part of these materials for teaching, commercial, or derivative
purposes is not allowed without written permission.
 
© 2026 TechUpSkills / Brent Laster. All rights reserved.
