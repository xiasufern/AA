import requests
import re
from datetime import datetime

# JULI Worker URL
JULI_SUB_URL = "https://smt-proxy.sufern001.workers.dev"
DD_FILE = "DD.m3u"

def fetch(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text

def extract_strict_juli(text):
    lines = text.splitlines()
    juli_lines = []
    capture = False
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")  # UTC 时间戳

    for line in lines:
        # 只抓 group-title="JULI" 的条目
        if line.startswith("#EXTINF:") and re.search(r'group-title=["\']JULI["\']', line, re.IGNORECASE):
            capture = True
            # 替换为 HK，并在频道名称后加时间戳
            line = re.sub(r'group-title=["\'].*?["\']', 'group-title="HK"', line)
            line += f' [{now_str}]'
            juli_lines.append(line)
            continue

        # URL 行，只有 capture=True 且包含 JULI 特征才抓
        if capture and line.strip() != "":
            if 'jackstar.php' in line or 'tg_Thinkoo_bot' in line:
                juli_lines.append(line)
            capture = False

    return "\n".join(juli_lines)

def main():
    print("[+] Fetch JULI subscription")
    juli_raw = fetch(JULI_SUB_URL)
    juli_only = extract_strict_juli(juli_raw)

    with open(DD_FILE, "w", encoding="utf-8") as f:
        f.write(juli_only + "\n")

    print(f"[✓] Generated {DD_FILE} (strict JULI → HK with timestamp)")

if __name__ == "__main__":
    main()
