#!/usr/bin/env bash
set -euo pipefail

# ---- Install Ollama only if not already present (pre-built image has it) ----
if command -v ollama >/dev/null 2>&1; then
  echo "Ollama already installed: $(ollama --version)"
else
  # Ensure prerequisites for install
  if ! command -v zstd >/dev/null 2>&1; then
    echo "Installing zstd..."
    if command -v apt-get >/dev/null 2>&1; then
      sudo apt-get update -y
      sudo apt-get install -y zstd curl ca-certificates
    elif command -v dnf >/dev/null 2>&1; then
      sudo dnf install -y zstd curl ca-certificates
    elif command -v yum >/dev/null 2>&1; then
      sudo yum install -y zstd curl ca-certificates
    elif command -v pacman >/dev/null 2>&1; then
      sudo pacman -Sy --noconfirm zstd curl ca-certificates
    else
      echo "ERROR: Unsupported package manager. Install 'zstd' manually and rerun."
      exit 1
    fi
  fi

  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh

  if ! command -v ollama >/dev/null 2>&1; then
    echo "ERROR: ollama is still not on PATH after install."
    echo "Try: ls -l /usr/local/bin/ollama && echo \$PATH"
    exit 1
  fi
fi

