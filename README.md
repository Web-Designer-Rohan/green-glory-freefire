# Free Fire Guest ID Generator - Free Termux Edition

This script runs directly on Android devices via Termux using **your own device's IP** (No external proxies needed).

## Features:
- 100% Free - uses your device's direct network connection.
- Supports 11 Free Fire regions (IND, BD, PK, ID, VN, TH, BR, ME, CIS, SAC, TW).
- Auto-generates unique in-game names and passwords.
- Real-time output with progress counter.
- Saves accounts automatically to `accounts.txt` and `accounts_REGION_TIMESTAMP.json`.

---

## How to Run in Termux:

### Step 1: Open Termux and Install Dependencies
```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install requests pycryptodome urllib3
```
*(Or simply run `bash setup.sh`)*

### Step 2: Run the Generator
```bash
python main.py
```

### Step 3:
1. Select your target region (e.g. `1` for India / INR).
2. Enter the number of guest accounts you want.
3. Done! Accounts will be generated and saved.

> **💡 Pro Tip:** If Garena shows rate-limit, simply turn **Airplane Mode ON for 5 seconds** and then turn it **OFF**. Your mobile carrier (Jio/Airtel/Vi) will assign you a new IP instantly, allowing you to generate more accounts right away!
