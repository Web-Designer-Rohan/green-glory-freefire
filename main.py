#!/usr/bin/env python3
"""
Free Fire Guest ID Generator - Free Termux Script
Runs directly in Termux using your device's own public IP (No proxy required).
Default Name & Password: kaddu yt
Saved Folder: kaddu yt/
"""

import sys
import os
import json
import time
import hmac
import hashlib
import string
import random
import urllib3
import requests
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== ANSI COLORS ====================
RED     = "\033[1;31m"
GREEN   = "\033[1;32m"
YELLOW  = "\033[1;33m"
BLUE    = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN    = "\033[1;36m"
WHITE   = "\033[1;37m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

# ==================== CRYPTO CONSTANTS ====================
HEX_KEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
API_KEY = HEX_KEY.encode()
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
GGRE_TOKEN = bytes.fromhex(
    "47475245010101006b0200008ed1eef0b8732739d0e3a17e6660d5ec5d31d9d7dd5b461085e403b4d942d4d3"
    "62cef18a7dbb4c27e5480e9ce49fec7a4e4eccbf8981e25013af12e9c2aacb9028c8239368ff7683e822684b"
    "b9b597e4c67973ca9104a9733f7fccdae9de785253e3246781bdfd6355e84637083ffe8536c61fc9aa00ccb1"
    "88ed4aac8d4a6976c09a0ef130fe6b78fb7a4fcfcc1aa5cb66c877079c663b874e8f6b728721e0f0c6706207"
    "684b71fe048216b660fad2c3a735c1176f820ab9ef190343eb88468365089641a5fb1de69ac6447e07b39ea6"
    "7d6d8ba2e65d601610902f83414cfee8d4f3e30440b6b248a40111aced9abb12800f4dfaabb47201c46b0793"
    "05a65b0f7af27a3fc40234c8b20d248e8abe2e3b3e721c203e001be1bcccb935076f56b78abd76f2e3a89a79"
    "22668dcacb3e20a8ac63de33ccef3c5976934fbba6bb95128cc5b7677cea4c4bd3957664aba3481ccb861773"
    "05aa6263ee0e13f468bbdba8ccd74fe8880e0711eecad62aefa61eb8c7085e80e033b39a0a07db2fd1a444cd"
    "9cb88008baa2f827cac1a331a06e7b40d098436ee7ab47a1b9387db295123a9472c9c3ba2922bd50811f6183"
    "330e955e938f67e6a899d18dea5905f7f4f5ce644c87a2347cde6b5092d0be2a3e65a774652d350289f1135e"
    "825642e194572b62e27e2931408c08b3c7f7fd3d31eff7c9dcc8beac4fe6675188992eb31944acf5cbbeaee3"
    "6d293a2cdde1c397f9c0766aa73104218f4fea20608155f5ac761ff9940e13e4a1543856bd1246407e1f837d"
    "f0473fe95d6333faa2aecf2ac5498222a082a0420d334e7f337525b20837726dd0b386ea85f0d4ae3bc552ff"
    "9b95579fc6bad84c52abef920cb684467edf6eb41285198395860233c89b6bbf709cb3a8bdec7b77a4ac5b4d"
    "9f27acfed16c4690c53a1c"
)

# Supported Regions
REGIONS = {
    "1": ("IND", "India"),
    "2": ("BD", "Bangladesh"),
    "3": ("PK", "Pakistan"),
    "4": ("ID", "Indonesia"),
    "5": ("VN", "Vietnam"),
    "6": ("TH", "Thailand"),
    "7": ("BR", "Brazil"),
    "8": ("ME", "Middle East"),
    "9": ("CIS", "Russia / CIS"),
    "10": ("SAC", "South America"),
    "11": ("TW", "Taiwan")
}

def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")

def get_device_public_ip():
    """Detects and returns user's real public device IP"""
    services = [
        "https://api.ipify.org?format=json",
        "https://ifconfig.me/all.json",
        "https://ipinfo.io/json"
    ]
    for url in services:
        try:
            r = requests.get(url, timeout=4)
            if r.status_code == 200:
                data = r.json()
                return data.get("ip") or data.get("ip_addr")
        except Exception:
            continue
    return "Direct Device IP"

# ==================== ANTI-TAMPER INTEGRITY ENGINE ====================
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/results?search_query=kadduyt"
OFFICIAL_YT_HASH = "2b67efb8e9fc5138bc17a1777ad8027ebd8e46e9dd4775704bed7a2b4a9a8fc2"

def verify_script_integrity():
    """Detects any modification or bypass of the YouTube link and terminates execution if tampered"""
    actual_hash = hashlib.sha256(YOUTUBE_CHANNEL_URL.strip().encode()).hexdigest()
    if actual_hash != OFFICIAL_YT_HASH or "kadduyt" not in YOUTUBE_CHANNEL_URL:
        clear_screen()
        print(f"\033[1;31m{'='*60}\033[0m")
        print(f"\033[1;31m\033[1m [X] TAMPER DETECTED: SCRIPT EXECUTION BLOCKED! \033[0m")
        print(f"\033[1;31m{'='*60}\033[0m")
        print(f"\033[1;33m [!] Error:\033[0m Unauthorized modification detected in YouTube link.")
        print(f"\033[1;37m [!] You are NOT allowed to edit, replace, or bypass the Kaddu YT channel link.\033[0m")
        print(f"\033[1;36m [*] Official Link: https://www.youtube.com/results?search_query=kadduyt\033[0m")
        print(f"\033[1;31m{'='*60}\033[0m\n")
        time.sleep(2)
        sys.exit(1)

def check_first_time_subscription():
    """Opens Kaddu YT YouTube channel on first run and asks user to subscribe to unlock the script"""
    verify_script_integrity()
    marker_home = os.path.expanduser("~/.kaddu_yt_subscribed")
    marker_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".subscribed")
    
    if os.path.exists(marker_home) or os.path.exists(marker_local):
        return
        
    clear_screen()
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{WHITE}       FIRST TIME USER VERIFICATION - KADDU YT        {RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{YELLOW} [*] Welcome to Free Fire Guest ID Generator!{RESET}")
    print(f"{WHITE} [*] Pehli baar use karne ke liye channel subscribe karna zaroori hai.{RESET}")
    print(f"{GREEN} [►] Opening YouTube Channel: Kaddu YT (@kaddu_yt9)...{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    yt_url = YOUTUBE_CHANNEL_URL
    
    # 1. Try Termux/Android am intent
    try:
        os.system(f"am start -a android.intent.action.VIEW -d '{yt_url}' >/dev/null 2>&1")
    except Exception:
        pass
    # 2. Try Termux API
    try:
        os.system(f"termux-open-url '{yt_url}' >/dev/null 2>&1")
    except Exception:
        pass
    # 3. Try xdg-open
    try:
        os.system(f"xdg-open '{yt_url}' >/dev/null 2>&1")
    except Exception:
        pass
    # 4. Try Python webbrowser
    try:
        import webbrowser
        webbrowser.open(yt_url)
    except Exception:
        pass
        
    print(f"{YELLOW}Agar YouTube auto-open na hua ho, toh is link ko open karein:{RESET}")
    print(f"{CYAN}👉 https://www.youtube.com/results?search_query=kadduyt{RESET}\n")
    
    try:
        input(f"{GREEN}{BOLD}👉 Channel subscribe karne ke baad [ENTER] dabayein to continue... {RESET}")
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)
        
    try:
        with open(marker_home, "w", encoding="utf-8") as f:
            f.write("subscribed")
    except Exception:
        pass
    try:
        with open(marker_local, "w", encoding="utf-8") as f:
            f.write("subscribed")
    except Exception:
        pass
        
    print(f"\n{GREEN}[✔] Thank you for subscribing! Loading script...{RESET}\n")
    time.sleep(1.5)

def print_banner(user_ip):
    clear_screen()
    print(f"{CYAN}{'='*58}{RESET}")
    print(f"{BOLD}{WHITE}     FREE FIRE GUEST ID GENERATOR - TERMUX (FREE)     {RESET}")
    print(f"{CYAN}{'='*58}{RESET}")
    print(f"{YELLOW} [*] Mode:{RESET} Direct Device Connection ({GREEN}Free Edition{RESET})")
    print(f"{YELLOW} [*] Your Device IP:{RESET} {CYAN}{user_ip}{RESET}")
    print(f"{YELLOW} [*] Default Identity:{RESET} {GREEN}kaddu yt{RESET}")
    print(f"{YELLOW} [*] Saved Folder:{RESET} {MAGENTA}kaddu yt/{RESET}")
    print(f"{CYAN}{'='*58}{RESET}\n")

# ==================== PROTOBUF & CRYPTO UTILS ====================
def create_vr(N):
    if N < 0: return b''
    H = []
    while True:
        S = N & 0x7F
        N >>= 7
        if N: S |= 0x80
        H.append(S)
        if not N: break
    return bytes(H)

def create_variant(field_number, value):
    return create_vr((field_number << 3) | 0) + create_vr(value)

def create_length(field_number, value):
    encoded_value = value.encode() if isinstance(value, str) else value
    return create_vr((field_number << 3) | 2) + create_vr(len(encoded_value)) + encoded_value

def create_proto(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            packet.extend(create_length(field, create_proto(value)))
        elif isinstance(value, int):
            packet.extend(create_variant(field, value))
        elif isinstance(value, (str, bytes)):
            packet.extend(create_length(field, value))
    return packet

def decode_varint(data, offset):
    result, shift = 0, 0
    while offset < len(data):
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80):
            return result, offset
        shift += 7
    return None, offset

def decode_protobuf(data):
    result, offset, data_len = {}, 0, len(data)
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None: break
        field_number, wire_type = header >> 3, header & 0x7
        if wire_type == 0:
            val, offset = decode_varint(data, offset)
            if val is not None: result[field_number] = val
        elif wire_type == 2:
            length, offset = decode_varint(data, offset)
            if length is None: break
            value = data[offset:offset + length]
            offset += length
            try:
                result[field_number] = value.decode('utf-8')
            except Exception:
                result[field_number] = value.hex()
        elif wire_type == 1: offset += 8
        elif wire_type == 3: offset += 4
        else: break
    return result

def aes_encrypt(hex_str):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(bytes.fromhex(hex_str), AES.block_size)).hex()

def generate_random_password(prefix="kaddu_yt"):
    code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    clean_prefix = str(prefix).strip().replace(" ", "_")
    clean_prefix = clean_prefix[:10]  # Ensure within Garena 16-char password limit
    return f"{clean_prefix}_{code}"

def generate_random_name(prefix="kaddu_yt"):
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    clean_prefix = str(prefix).strip().replace(" ", "_")
    clean_prefix = clean_prefix[:7]   # Ensure total nickname length <= 12 chars
    return f"{clean_prefix}{suffix}"

# ==================== CORE API CALLS ====================
def register_account(password, session):
    verify_script_integrity()
    url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
    payload_json = {"app_id": 100067, "client_type": 2, "password": password, "source": 2, "sdk_version": "2.0.0"}
    payload = json.dumps(payload_json, separators=(',', ':'))
    signature = hmac.new(API_KEY, payload.encode(), hashlib.sha256).hexdigest()
    timestamp = str(int(time.time()))
    
    headers = {
        "User-Agent": f"Dalvik/2.1.0 (Linux; U; Android {random.randint(9, 14)}; SM-G960F)",
        "Authorization": f"Signature {signature}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "Host": "100067.connect.garena.com",
        "X-Garena-Timestamp": timestamp
    }
    try:
        response = session.post(url, headers=headers, data=payload, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0 and "data" in data:
                return data["data"]["uid"], password, False
            elif data.get("code") == 1006:
                return None, None, True
        elif response.status_code == 429:
            return None, None, True
    except Exception:
        pass
    return None, None, False

def get_access_token(uid, password, session):
    try:
        url = "https://ffmconnect.live.gop.garenanow.com/api/v2/oauth/guest/token:grant"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Host": "ffmconnect.live.gop.garenanow.com",
            "User-Agent": "GarenaMSDK/4.0.44(SM-G965N ;Android 7.1.2;en;US;app 2.133.1 2019118527;)"
        }
        body = {
            "client_id": 100067,
            "client_secret": HEX_KEY,
            "client_type": 2,
            "device_id": "",
            "password": password,
            "response_type": "token",
            "uid": uid
        }
        response = session.post(url, headers=headers, json=body, timeout=8)
        if response.status_code == 200:
            data = response.json().get("data", {})
            if "access_token" in data:
                return data.get("access_token"), data.get("open_id")
    except Exception:
        pass

    try:
        url_fb = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers_fb = {
            "Host": "100067.connect.garena.com",
            "User-Agent": f"Dalvik/2.1.0 (Linux; U; Android {random.randint(9, 14)}; SM-G960F)",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data_fb = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": HEX_KEY,
            "client_id": "100067"
        }
        response = session.post(url_fb, headers=headers_fb, data=data_fb, timeout=8)
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get("access_token"), json_data.get("open_id")
    except Exception:
        pass
    return None, None

def major_register(access_token, open_id, name, session):
    url = "https://loginbp.ppmainecoonghj.com/MajorRegister"
    keystream = [0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37,
                 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30]
    encoded_open_id = bytes([ord(ch) ^ keystream[i % len(keystream)] for i, ch in enumerate(open_id)])
    
    payload_fields = {
        1: name,
        2: access_token,
        3: open_id,
        5: 102000007,
        6: 4,
        7: 1,
        13: 1,
        14: encoded_open_id,
        15: "en",
        16: 2,
        20: "2.133.9",
        21: 1,
        22: GGRE_TOKEN
    }
    payload = bytes.fromhex(aes_encrypt(create_proto(payload_fields).hex()))
    headers = {
        "Accept": "*/*",
        "Authorization": "Bearer",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "loginbp.ppmainecoonghj.com",
        "ReleaseVersion": "OB55",
        "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "X-GA": "v1 1",
        "X-GA-SV": "1791730008",
        "X-Unity-Version": "2018.4.12f1"
    }
    try:
        response = session.post(url, headers=headers, data=payload, timeout=8)
        if response.status_code == 200:
            decoded = decode_protobuf(response.content)
            if 3 in decoded:
                return decoded
            if 9 in decoded:
                payload_fields[1] = decoded[9]
                alt_payload = bytes.fromhex(aes_encrypt(create_proto(payload_fields).hex()))
                alt_resp = session.post(url, headers=headers, data=alt_payload, timeout=8)
                if alt_resp.status_code == 200:
                    alt_decoded = decode_protobuf(alt_resp.content)
                    if 3 in alt_decoded:
                        return alt_decoded
    except Exception:
        pass
    return {}

def create_account(session, custom_name="kaddu_yt", custom_password="kaddu_yt"):
    password = generate_random_password(custom_password or "kaddu_yt")
    
    reg_uid, registered_pass, is_rate_limited = register_account(password, session)
    if is_rate_limited:
        return None, "Device IP rate limited by Garena. Wait 1-2 minutes or switch airplane mode."
    if not reg_uid:
        return None, "Registration request failed."
        
    password = registered_pass
    access_token, open_id = get_access_token(reg_uid, password, session)
    if not access_token:
        return None, "Failed to retrieve access token."
        
    name = generate_random_name(custom_name or "kaddu_yt")
    reg_response = major_register(access_token, open_id, name, session)
    if not reg_response or 3 not in reg_response:
        return None, "Failed during MajorRegister step."
        
    account_id = str(reg_response[3])
    final_name = reg_response.get(9, name)
    
    return {
        "game_id": account_id,
        "garena_uid": reg_uid,
        "name": final_name,
        "password": password,
        "access_token": access_token
    }, None

# ==================== MAIN CLI ====================
def main():
    check_first_time_subscription()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "kaddu yt")
    os.makedirs(output_dir, exist_ok=True)
    
    user_ip = get_device_public_ip()
    print_banner(user_ip)
    
    print(f"{BOLD}{WHITE}Available Regions:{RESET}")
    for key, (code, label) in REGIONS.items():
        print(f"  {CYAN}[{key}]{RESET} {code} - {label}")
    print()
    
    region_choice = input(f"{YELLOW}Select Region [default: 1 for IND]: {RESET}").strip() or "1"
    selected_region, region_name = REGIONS.get(region_choice, ("IND", "India"))
    
    try:
        qty_input = input(f"{YELLOW}How many guest IDs to generate? [e.g. 1]: {RESET}").strip()
        count = int(qty_input) if qty_input else 1
    except ValueError:
        count = 1
        
    # Free script default is always "kaddu yt"
    custom_name = input(f"{YELLOW}ID Name Prefix [Default: kaddu yt]: {RESET}").strip() or "kaddu_yt"
    custom_pass = input(f"{YELLOW}Password Prefix [Default: kaddu yt]: {RESET}").strip() or "kaddu_yt"
    
    print(f"\n{GREEN}[+] Starting generator on your device IP: {user_ip}{RESET}")
    print(f"{GREEN}[+] Target Region: {selected_region} ({region_name}) | Total: {count}{RESET}")
    print(f"{GREEN}[+] Default Name/Pass: {custom_name}{RESET}")
    print(f"{MAGENTA}[+] Output Directory: {output_dir}{RESET}\n")
    
    session = requests.Session()
    session.verify = False
    
    generated_accounts = []
    accounts_txt_path = os.path.join(output_dir, "accounts.txt")
    
    for i in range(1, count + 1):
        print(f"{YELLOW}[~] [{i}/{count}] Generating guest account...{RESET}", end="\r")
        acc, err = create_account(session, custom_name, custom_pass)
        
        if acc:
            generated_accounts.append(acc)
            print(f"{GREEN}[✔] [{i}/{count}] UID: {acc['game_id']} | Pass: {acc['password']} | Name: {acc['name']}{RESET}")
            
            # Append immediately to kaddu yt/accounts.txt
            with open(accounts_txt_path, "a", encoding="utf-8") as f:
                f.write(f"{acc['garena_uid']}:{acc['password']} | GameID: {acc['game_id']} | Name: {acc['name']} | Region: {selected_region}\n")
        else:
            print(f"{RED}[✘] [{i}/{count}] Failed: {err}{RESET}")
            if "rate limited" in str(err).lower():
                print(f"{YELLOW}[!] Tip: Toggle Airplane mode for 5 seconds to get a fresh mobile IP from your telecom provider.{RESET}")
                break
        time.sleep(0.5)
        
    if generated_accounts:
        # Save JSON output in kaddu yt folder
        out_json_filename = f"accounts_{selected_region}_{int(time.time())}.json"
        out_json_path = os.path.join(output_dir, out_json_filename)
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "region": selected_region,
                "total": len(generated_accounts),
                "device_ip": user_ip,
                "accounts": generated_accounts
            }, f, indent=2)
            
        print(f"\n{CYAN}{'='*58}{RESET}")
        print(f"{GREEN}{BOLD}🎉 GENERATION COMPLETED!{RESET}")
        print(f"{WHITE}Total Generated: {len(generated_accounts)}/{count}{RESET}")
        print(f"{MAGENTA}Output Folder:{RESET} kaddu yt/")
        print(f"{GREEN}Saved Combos:{RESET} {accounts_txt_path}")
        print(f"{GREEN}Saved Full JSON:{RESET} {out_json_path}")
        print(f"{CYAN}{'='*58}{RESET}\n")
    else:
        print(f"\n{RED}[!] No accounts could be generated.{RESET}\n")

if __name__ == "__main__":
    main()
