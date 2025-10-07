#!/usr/bin/env python3
"""
Hugging Face Spaces Startup Script
==================================

This script starts both the MCP server and Streamlit app for deployment
on Hugging Face Spaces. It handles:
- Starting MCP server in background
- Starting Streamlit app on the correct port
- Proper process management and cleanup
- Health checks and error handling
"""

import os
import sys
import time
import signal
import subprocess
import threading
import requests
from pathlib import Path

# Configuration
MCP_SERVER_PORT = 8000
STREAMLIT_PORT = int(os.environ.get("PORT", 7860))  # HF Spaces uses port 7860
MCP_SERVER_SCRIPT = "mcp_server_classification.py"
STREAMLIT_SCRIPT = "streamlit_app.py"

class ProcessManager:
    def __init__(self):
        self.ollama_process = None
        self.mcp_process = None
        self.streamlit_process = None
        self.shutdown = False

    def start_ollama(self):
        """Start Ollama service and pull llama3.2 model."""
        print("Starting Ollama service...")
        try:
            # Get model from environment variable (default to llama3.2:1b for deployment)
            ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

            # Start Ollama server in background
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True
            )
            print(f"Ollama process started with PID: {self.ollama_process.pid}")

            # Monitor Ollama output
            def monitor_ollama():
                for line in iter(self.ollama_process.stderr.readline, ''):
                    if not self.shutdown:
                        print(f"[Ollama] {line.strip()}")

            threading.Thread(target=monitor_ollama, daemon=True).start()

            # Wait for Ollama to be ready
            print("⏳ Waiting for Ollama to start...")
            time.sleep(5)

            # Pull model specified by environment variable
            print(f"Pulling {ollama_model} model...")
            pull_result = subprocess.run(
                ["ollama", "pull", ollama_model],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for model download
            )

            if pull_result.returncode == 0:
                print(f"✅ {ollama_model} model ready")
                return True
            else:
                print(f"❌ Failed to pull {ollama_model} model: {pull_result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout pulling {ollama_model} model")
            return False
        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}")
            return False

    def start_mcp_server(self):
        """Start the MCP server in background."""
        print("Starting MCP server...")
        print(f"Python executable: {sys.executable}")
        print(f"MCP script: {MCP_SERVER_SCRIPT}")

        # Check if script exists
        if not Path(MCP_SERVER_SCRIPT).exists():
            print(f"ERROR: {MCP_SERVER_SCRIPT} not found!")
            return False

        try:
            self.mcp_process = subprocess.Popen(
                [sys.executable, "-u", MCP_SERVER_SCRIPT],  # -u for unbuffered output
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True
            )
            print(f"MCP process started with PID: {self.mcp_process.pid}")
            
            # Monitor MCP server output in separate threads
            def monitor_mcp_stdout():
                for line in iter(self.mcp_process.stdout.readline, ''):
                    if not self.shutdown:
                        print(f"[MCP] {line.strip()}")

            def monitor_mcp_stderr():
                for line in iter(self.mcp_process.stderr.readline, ''):
                    if not self.shutdown:
                        print(f"[MCP ERROR] {line.strip()}")

            threading.Thread(target=monitor_mcp_stdout, daemon=True).start()
            threading.Thread(target=monitor_mcp_stderr, daemon=True).start()

            # Give it a moment to fail if there's an immediate error
            time.sleep(2)

            # Check if process is still alive
            if self.mcp_process.poll() is not None:
                print(f"❌ MCP server process died immediately with exit code: {self.mcp_process.returncode}")
                # Try to read any remaining output
                remaining_stdout = self.mcp_process.stdout.read()
                remaining_stderr = self.mcp_process.stderr.read()
                if remaining_stdout:
                    print(f"[MCP STDOUT] {remaining_stdout}")
                if remaining_stderr:
                    print(f"[MCP STDERR] {remaining_stderr}")
                return False

            # Wait for MCP server to be ready
            self.wait_for_mcp_server()
            print("✅ MCP server is ready")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    def wait_for_mcp_server(self, max_attempts=60):
        """Wait for MCP server to be ready."""
        for attempt in range(max_attempts):
            try:
                # Just check if the server is running by trying to connect
                # We don't need a valid MCP message, just check if port is open
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', MCP_SERVER_PORT))
                sock.close()

                if result == 0:  # Port is open
                    print(f"✅ MCP server port {MCP_SERVER_PORT} is open")
                    return True
            except Exception as e:
                if attempt % 5 == 0:  # Print every 5 attempts
                    print(f"⏳ Waiting for MCP server... ({attempt + 1}/{max_attempts}) - {e}")

            time.sleep(1)

        raise Exception("MCP server failed to start within timeout period")
    
    def start_streamlit_app(self):
        """Start the Streamlit application."""
        print("🚀 Starting Streamlit app...")
        try:
            # Streamlit command for Hugging Face Spaces
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                STREAMLIT_SCRIPT,
                "--server.port", str(STREAMLIT_PORT),
                "--server.address", "0.0.0.0",
                "--server.headless", "true",
                "--server.fileWatcherType", "none",
                "--browser.gatherUsageStats", "false"
            ]
            
            self.streamlit_process = subprocess.Popen(cmd)
            print(f"✅ Streamlit app started on port {STREAMLIT_PORT}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Streamlit app: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes."""
        print("🧹 Cleaning up processes...")
        self.shutdown = True

        if self.ollama_process:
            try:
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=5)
                print("✅ Ollama stopped")
            except subprocess.TimeoutExpired:
                self.ollama_process.kill()
                print("⚠️ Ollama force killed")
            except Exception as e:
                print(f"⚠️ Error stopping Ollama: {e}")

        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
                print("✅ MCP server stopped")
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()
                print("⚠️ MCP server force killed")
            except Exception as e:
                print(f"⚠️ Error stopping MCP server: {e}")
        
        if self.streamlit_process:
            try:
                self.streamlit_process.terminate()
                self.streamlit_process.wait(timeout=5)
                print("✅ Streamlit app stopped")
            except subprocess.TimeoutExpired:
                self.streamlit_process.kill()
                print("⚠️ Streamlit app force killed")
            except Exception as e:
                print(f"⚠️ Error stopping Streamlit app: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print(f"\nReceived signal {signum}, shutting down...")
    if 'manager' in globals():
        manager.cleanup()
    sys.exit(0)

def main():
    """Main startup function."""
    global manager
    
    print("Starting Hugging Face Spaces Application")
    print("=" * 50)
    print(f"MCP Server Port: {MCP_SERVER_PORT}")
    print(f"Streamlit Port: {STREAMLIT_PORT}")
    print("=" * 50)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if required files exist
    if not Path(MCP_SERVER_SCRIPT).exists():
        print(f"❌ Error: {MCP_SERVER_SCRIPT} not found")
        sys.exit(1)
    
    if not Path(STREAMLIT_SCRIPT).exists():
        print(f"❌ Error: {STREAMLIT_SCRIPT} not found")
        sys.exit(1)
    
    # Start process manager
    manager = ProcessManager()

    try:
        # Start Ollama first
        if not manager.start_ollama():
            print("❌ Failed to start Ollama")
            sys.exit(1)

        # Start MCP server
        if not manager.start_mcp_server():
            print("❌ Failed to start MCP server")
            manager.cleanup()
            sys.exit(1)
        
        # Start Streamlit app
        if not manager.start_streamlit_app():
            print("❌ Failed to start Streamlit app")
            manager.cleanup()
            sys.exit(1)
        
        print("🎉 Both services are running!")
        print(f"📱 Access the app at: http://localhost:{STREAMLIT_PORT}")
        print("⏹️ Press Ctrl+C to stop all services")
        
        # Keep the main process alive and monitor subprocesses
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if manager.mcp_process and manager.mcp_process.poll() is not None:
                print("⚠️ MCP server process died, restarting...")
                if not manager.start_mcp_server():
                    print("❌ Failed to restart MCP server")
                    break
            
            if manager.streamlit_process and manager.streamlit_process.poll() is not None:
                print("⚠️ Streamlit process died")
                break
    
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        manager.cleanup()
        print("Goodbye!")

if __name__ == "__main__":
    main()
