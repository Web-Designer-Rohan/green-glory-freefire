#!/usr/bin/env python3
"""OB55 Multi-Account Manifest Manager & Automated Guest Generator"""
import sys
import os
import json
import time
import hmac
import hashlib
import string
import random
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

RELEASE_VERSION = "OB55"
LOGIN_URL = "https://loginbp.ppmainecoonghj.com/MajorLogin"
REGISTER_URL = "https://loginbp.ppmainecoonghj.com/MajorRegister"
USER_AGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
REQUEST_TIMEOUT = 10
MANIFEST_DIR = "kaddu yt"

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

def aes_encrypt(hex_str):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(bytes.fromhex(hex_str), AES.block_size)).hex()

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

def generate_random_password(prefix="kaddu_yt"):
    code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix.strip()}_{code}"

def generate_random_name(prefix="kaddu_yt"):
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix[:7]}{suffix}"

def save_account_manifest(uid, password, access_token, open_id):
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    manifest_path = os.path.join(MANIFEST_DIR, f"account_{uid}.json")
    account_data = {
        "uid": uid,
        "password": password,
        "access_token": access_token,
        "open_id": open_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(account_data, f, indent=2)
    print(f" [✔] Account manifest saved successfully: {manifest_path}")

def register_fresh_guest(session):
    print(" [*] Registering fresh guest account with Garena...")
    password = generate_random_password()
    url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
    payload_json = {"app_id": 100067, "client_type": 2, "password": password, "source": 2, "sdk_version": "2.0.0"}
    payload = json.dumps(payload_json, separators=(',', ':'))
    signature = hmac.new(API_KEY, payload.encode(), hashlib.sha256).hexdigest()
    timestamp = str(int(time.time()))

    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-G960F)",
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
                uid = data["data"]["uid"]
                print(f" [✔] Guest registered successfully. UID: {uid}")
                return str(uid), password
    except Exception as e:
        print(f" [!] Registration exception: {e}")
    return None, None

def get_access_token(uid, password, session):
    print(" [*] Requesting access token for guest (Primary endpoint)...")
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
                token = data.get("access_token")
                openid = data.get("open_id")
                print(f" [✔] Access token acquired (Primary): {token[:16]}...")
                return token, str(openid or uid)
    except Exception:
        pass

    print(" [*] Trying fallback access token endpoint...")
    try:
        url_fb = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers_fb = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-G960F)",
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
            token = json_data.get("access_token")
            openid = json_data.get("open_id")
            if token:
                print(f" [✔] Access token acquired (Fallback): {token[:16]}...")
                return token, str(openid or uid)
    except Exception as e:
        print(f" [!] Fallback token grant exception: {e}")

    return None, None

def perform_major_register(access_token, open_id, session):
    print(" [*] Registering account on OB55 Gateway (MajorRegister)...")
    name = generate_random_name()
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
        "ReleaseVersion": RELEASE_VERSION,
        "User-Agent": USER_AGENT,
        "X-GA": "v1 1",
        "X-GA-SV": "1791730008",
        "X-Unity-Version": "2018.4.12f1"
    }
    try:
        response = session.post(REGISTER_URL, headers=headers, data=payload, timeout=8)
        print(f" [✔] MajorRegister HTTP Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f" [!] MajorRegister exception: {e}")
        return False

def send_login_request():
    print(f"\n{'-'*55}")
    print(f" [*] Automated OB55 End-to-End Guest Registration & Manifest Manager")
    print(f" [*] Target Endpoint : {LOGIN_URL}")
    print(f"{'-'*55}")

    session = requests.Session()
    uid, password = register_fresh_guest(session)
    if not uid:
        return {"success": False, "error_type": "REG_ERROR", "error": "Failed to register fresh guest account."}

    token, open_id = get_access_token(uid, password, session)
    if not token:
        return {"success": False, "error_type": "TOKEN_ERROR", "error": "Failed to obtain guest access token."}

    # Save manifest automatically
    save_account_manifest(uid, password, token, open_id)

    perform_major_register(token, open_id, session)

    try:
        from proto import FreeFire_pb2
        login_req = FreeFire_pb2.LoginReq()
        login_req.login_token = token
        login_req.open_id = open_id
        login_req.open_id_type = "2"
        login_req.orign_platform_type = "4"

        print(f" [✔] Assembled LoginReq protobuf packet.")

        raw_proto = login_req.SerializeToString()
        encrypted_payload = bytes.fromhex(aes_encrypt(raw_proto.hex()))
        print(f" [✔] Serialized and AES-encrypted payload ({len(encrypted_payload)} bytes).")
    except Exception as e:
        return {"success": False, "error_type": "PROTO_SERIALIZE_ERROR", "error": str(e)}

    headers = {
        "Accept": "*/*",
        "Authorization": "Bearer",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "loginbp.ppmainecoonghj.com",
        "ReleaseVersion": RELEASE_VERSION,
        "User-Agent": USER_AGENT,
        "X-GA": "v1 1",
        "X-GA-SV": "1791730008",
        "X-Unity-Version": "2018.4.12f1"
    }

    print(f" [~] Dispatching request to login gateway...")
    try:
        response = requests.post(LOGIN_URL, headers=headers, data=encrypted_payload, timeout=REQUEST_TIMEOUT)
        print(f" [✔] HTTP Response received. Status Code: {response.status_code}")
        print(f" [✔] Response content length: {len(response.content)} bytes")

        if response.status_code == 200:
            return {
                "success": True,
                "status_code": 200,
                "uid": uid,
                "manifest_saved": True,
                "authentication_verified": True
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error_type": f"HTTP_{response.status_code}",
                "error": f"Gateway rejected request with HTTP status {response.status_code}.",
                "response_body": response.content.decode('utf-8', errors='ignore')
            }

    except requests.exceptions.Timeout:
        return {"success": False, "error_type": "TIMEOUT_ERROR", "error": "Request timed out."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error_type": "CONNECTION_ERROR", "error": "Connection failed."}
    except Exception as e:
        return {"success": False, "error_type": "UNEXPECTED_EXCEPTION", "error": str(e)}

if __name__ == "__main__":
    result = send_login_request()
    print(json.dumps(result, indent=2))
