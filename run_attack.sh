#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

echo "[*] Starting CTF CAPTCHA Server..."
python server/main.py &
SERVER_PID=$!

echo "[*] Waiting for server to initialize..."
sleep 3

echo "[*] Launching Auto Solver..."
python solver/exploit.py

echo "[*] Exploit finished or interrupted. Shutting down server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null
echo "[*] Server stopped."
