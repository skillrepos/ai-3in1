Local setup mac · MD
# Local Setup for Mac (No Codespace / No Docker / No Dev Container)
 
### NOTE: GitHub Codespaces — as detailed in the README.md file — are the preferred and recommended environment for these labs. Use this guide only if you can't use a Codespace and can't run the Dev Container locally either.
 
This guide sets up everything the labs need directly on your Mac — no Docker, no Dev Containers extension. You'll install Python, Ollama, Git, and a couple of small CLI tools, then run the labs from Terminal.
 
<br>
**Instructions below use Terminal** (Applications → Utilities → Terminal, or search for it with Spotlight).
 
---
 
## 1. (Recommended) Install Homebrew
 
[Homebrew](https://brew.sh) makes the rest of this much easier. If you don't already have it:
 
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
 
Follow any on-screen instructions to add `brew` to your PATH, then verify:
```bash
brew --version
```
 
If you'd rather not use Homebrew, you can install each tool below via its own installer package instead — links are included.
 
<br>
## 2. Install Git
 
Most Macs already have Git (via Xcode Command Line Tools). Check first:
```bash
git --version
```
If that prompts you to install the Command Line Tools, accept — that installs Git. Otherwise, install/update via Homebrew:
```bash
brew install git
```
Or download an installer from [git-scm.com](https://git-scm.com).
 
<br>
## 3. Install Python 3.11
 
```bash
brew install python@3.11
```
Or download the macOS installer from [python.org/downloads](https://www.python.org/downloads/). (3.10–3.12 will also work; the workshop's Docker image is built on Python 3.11.)
 
Verify:
```bash
python3 --version
pip3 --version
```
 
<br>
## 4. Install jq
 
One lab step uses `jq` to pretty-print JSON from a `curl` call.
```bash
brew install jq
```
Verify:
```bash
jq --version
```
 
<br>
## 5. Install Ollama
 
```bash
brew install ollama
```
Or download the macOS app from [ollama.com/download](https://ollama.com/download) and drag it to Applications.
 
If you installed the `.app` version, opening it once will place an Ollama icon in the menu bar and start serving on `http://localhost:11434` automatically — you usually do **not** need to run `ollama serve` yourself. If you installed via Homebrew, start it with:
```bash
ollama serve &
```
 
Verify:
```bash
ollama --version
ollama list
```
 
<br>
## 6. (Optional but recommended) Install VS Code
 
The labs use a "diff and merge" technique (`code -d file1 file2`) to build out code side-by-side. This works in a normal local install of VS Code — you do **not** need the Dev Containers extension or Docker for it.
 
```bash
brew install --cask visual-studio-code
```
Or download from [code.visualstudio.com](https://code.visualstudio.com/download).
 
Then, from within VS Code, open the Command Palette (Cmd+Shift+P), run **"Shell Command: Install 'code' command in PATH"**, and restart Terminal. Verify:
```bash
code --version
```
 
If you'd like the hover "thought bubble" comments that appear during the merge steps (shown in the labs.md screenshots), you can install the extension manually once you've cloned the repo (step 7 below):
```bash
code --install-extension ./.devcontainer/merge-info-0.1.0.vsix
```
This is cosmetic only — the merges themselves work fine without it.
 
<br>
## 7. Clone the repository
 
```bash
git clone https://github.com/skillrepos/ai-3in1
cd ai-3in1
```
 
<br>
## 8. Create a Python virtual environment and install dependencies
 
The workshop's Docker image installs CPU-only PyTorch *before* the rest of `requirements.txt` to keep things small and avoid pulling in GPU packages. Do the same locally:
 
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```
 
Each time you open a new Terminal to work on the labs, re-activate the environment:
```bash
cd ai-3in1
source .venv/bin/activate
```
 
<br>
## 9. Pull the model and warm everything up
 
```bash
ollama pull llama3.2
python warmup_models.py
```
 
This mirrors Lab 1's steps 4 and 12 and pre-loads the LLM and embedding model so the rest of the labs start quickly.
 
<br>
## 10. You're ready — follow labs.md
 
Open `labs.md` in VS Code (or your browser) and start at **Lab 1**. Everything in it runs the same way it does in the Codespace once your virtual environment is active and Ollama is running, with a couple of small notes:
 
- Wherever the lab says `ollama serve &`, skip it if Ollama is already running via the menu bar app (step 5); otherwise run it as written.
- `OLLAMA_KEEP_ALIVE=-1 ollama serve &` works as-is in Terminal (bash/zsh).
- The `curl ... | jq -r '.response'` command in Lab 1, step 7 works as written once `jq` is installed (step 4).
- Anywhere the lab references starting a second terminal (Lab 3, Lab 5), open a new Terminal tab/window, `cd` into the `ai-3in1` folder, and re-activate the virtual environment (`source .venv/bin/activate`) before running commands there.
<br>
## Troubleshooting
 
- **`command not found: ollama` / `python3` / `code`:** open a new Terminal window after installing (PATH changes need a fresh shell), or re-check that Homebrew's shell setup step from step 1 was completed.
- **Port 11434 already in use:** Ollama is likely already running via the menu bar app — you don't need to start it again.
- **`pip install` fails on `torch`:** make sure you ran the CPU-only `torch` install command in step 8 *before* `pip install -r requirements.txt`.
- **Apple Silicon (M-series) note:** everything here (Python, Ollama, PyTorch CPU wheels) has native Apple Silicon support — no Rosetta needed.
---
 
## License and Use
 
These materials are provided as part of the virtual training conducted by **TechUpSkills (Brent Laster)**.
 
Use of this repository is permitted **only for registered workshop participants** for their own personal learning and
practice. Redistribution, republication, or reuse of any part of these materials for teaching, commercial, or derivative
purposes is not allowed without written permission.
 
© 2026 TechUpSkills / Brent Laster. All rights reserved.
