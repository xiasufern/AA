import requests
import re

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

    for line in lines:
        # 只抓 URL 和 EXTINF 中有 "JULI" 或特定 ID 的条目
        if line.startswith("#EXTINF:") and ('JULI' in line.upper()):
            capture = True
            # 替换分组为 HK
            line = re.sub(r'group-title=["\'].*?["\']', 'group-title="HK"', line)
            juli_lines.append(line)
            continue

        # URL 行
        if capture and line.strip() != "":
            # 只抓 URL 中包含 jackstar.php 或 tg_Thinkoo_bot 的链接
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

    print(f"[✓] Generated {DD_FILE} (strict JULI → HK)")

if __name__ == "__main__":
    main()
