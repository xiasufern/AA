import requests
import re
from datetime import datetime
import os

# Worker URL
JULI_SUB_URL = "https://smt-proxy.sufern001.workers.dev"
EE_FILE = "EE.m3u"

def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36",
        "Accept": "*/*",
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"⚠️ Fetch failed: {e}")
        return ""

def extract_strict_juli(text):
    lines = text.splitlines()
    juli_lines = []
    capture = False
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    for line in lines:
        if line.startswith("#EXTINF:") and re.search(r'group-title=["\']JULI["\']', line, re.IGNORECASE):
            capture = True
            line = re.sub(r'group-title=["\'].*?["\']', 'group-title="HK"', line)
            line += f' [{now_str}]'
            juli_lines.append(line)
            continue
        if capture and line.strip() != "":
            juli_lines.append(line)
            capture = False

    return "\n".join(juli_lines)

def main():
    print("[+] Fetch JULI subscription")
    juli_raw = fetch(JULI_SUB_URL)
    if not juli_raw.strip():
        print("⚠️ JULI source empty, EE.m3u will be empty")
    juli_only = extract_strict_juli(juli_raw)

    # 覆盖写入 EE.m3u
    with open(EE_FILE, "w", encoding="utf-8") as f:
        f.write(juli_only + "\n")

    print(f"[✓] EE.m3u generated (strict JULI → HK, overwrite)")

if __name__ == "__main__":
    main()
