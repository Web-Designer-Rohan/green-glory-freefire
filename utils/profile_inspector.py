#!/usr/bin/env python3
"""OB55 Post-Login Profile Inspector using /GetPlayerPersonalShow"""
import sys
import os
import json
import glob
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

RELEASE_VERSION = "OB55"
PROFILE_URL = "https://loginbp.ppmainecoonghj.com/GetPlayerPersonalShow"
USER_AGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
REQUEST_TIMEOUT = 10
MANIFEST_DIR = "kaddu yt"

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def aes_encrypt(hex_str):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(bytes.fromhex(hex_str), AES.block_size)).hex()

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

def decode_protobuf_deep(data):
    result = {}
    offset = 0
    data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None: break
        field_number, wire_type = header >> 3, header & 0x7
        
        if wire_type == 0:
            val, offset = decode_varint(data, offset)
            if val is not None:
                result.setdefault(field_number, []).append(val)
        elif wire_type == 2:
            length, offset = decode_varint(data, offset)
            if length is None: break
            value = data[offset:offset + length]
            offset += length
            try:
                sub_decoded = decode_protobuf_deep(value)
                if sub_decoded and len(sub_decoded) > 0:
                    result.setdefault(field_number, []).append(sub_decoded)
                    continue
            except Exception:
                pass
            
            try:
                decoded_str = value.decode('utf-8')
                if all(ord(c) < 127 and c.isprintable() for c in decoded_str) and len(decoded_str) > 0:
                    result.setdefault(field_number, []).append(decoded_str)
                else:
                    result.setdefault(field_number, []).append(value.hex())
            except Exception:
                result.setdefault(field_number, []).append(value.hex())
        elif wire_type == 1:
            offset += 8
        elif wire_type == 3:
            offset += 4
        else:
            break
    return result

def get_latest_account():
    if not os.path.exists(MANIFEST_DIR):
        print(f" [!] Manifest directory '{MANIFEST_DIR}' not found.")
        return None
    
    manifest_files = glob.glob(os.path.join(MANIFEST_DIR, "account_*.json"))
    if not manifest_files:
        print(f" [!] No account manifests found.")
        return None
    
    latest_file = max(manifest_files, key=os.path.getmtime)
    print(f" [✔] Loaded latest account manifest: {latest_file}")
    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)

def inspect_profile():
    print(f"\n{'-'*55}")
    print(f" [*] OB55 Profile Inspector (/GetPlayerPersonalShow)")
    print(f" [*] Target Endpoint : {PROFILE_URL}")
    print(f"{'-'*55}")

    acc = get_latest_account()
    if not acc:
        return {"success": False, "error": "No account manifest available."}

    uid = acc.get("uid")
    token = acc.get("access_token")

    print(f" [✔] Target UID      = {uid}")
    print(f" [✔] Access Token    = {token[:16]}...")

    try:
        # Construct protobuf payload mapping UID (Field 1: int or string)
        # Using simple TLV encoding for field 1 (UID) and field 2 (unknown flag/type "7")
        uid_int = int(uid)
        
        # Helper to encode varint
        def encode_varint(n):
            b = bytearray()
            while True:
                to_write = n & 0x7f
                n >>= 7
                if n:
                    b.append(to_write | 0x80)
                else:
                    b.append(to_write)
                    break
            return bytes(b)

        payload_bytes = bytearray()
        # Field 1 (Variant/Int): UID
        payload_bytes.extend(bytes([(1 << 3) | 0]))
        payload_bytes.extend(encode_varint(uid_int))
        
        # Field 2 (Variant/Int): Region/Type flag "7"
        payload_bytes.extend(bytes([(2 << 3) | 0]))
        payload_bytes.extend(encode_varint(7))

        encrypted_payload = bytes.fromhex(aes_encrypt(payload_bytes.hex()))
        print(f" [✔] Serialized and encrypted profile payload ({len(encrypted_payload)} bytes).")
    except Exception as e:
        return {"success": False, "error": f"Payload construction failed: {str(e)}"}

    headers = {
        "Accept": "*/*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "loginbp.ppmainecoonghj.com",
        "ReleaseVersion": RELEASE_VERSION,
        "User-Agent": USER_AGENT,
        "X-GA": "v1 1",
        "X-GA-SV": "1791730008",
        "X-Unity-Version": "2018.4.12f1"
    }

    print(f" [~] Dispatching profile request to gateway...")
    try:
        response = requests.post(PROFILE_URL, headers=headers, data=encrypted_payload, timeout=REQUEST_TIMEOUT)
        print(f" [✔] HTTP Response received. Status Code: {response.status_code}")
        print(f" [✔] Response content length: {len(response.content)} bytes")

        if response.status_code == 200:
            decoded = decode_protobuf_deep(response.content)
            return {
                "success": True,
                "status_code": 200,
                "uid": uid,
                "profile_data": decoded
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": f"Gateway rejected request with HTTP status {response.status_code}.",
                "response_body": response.content.decode('utf-8', errors='ignore')
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = inspect_profile()
    print(json.dumps(result, indent=2))
