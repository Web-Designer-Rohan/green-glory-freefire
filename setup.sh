#!/bin/bash
echo "[+] Setting up Free Fire Guest ID Generator in Termux..."
pkg update -y
pkg install python -y
pip install --upgrade pip
pip install requests pycryptodome urllib3
echo "[✔] Setup completed successfully!"
echo "[*] Run the script using: python main.py"
