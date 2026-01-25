import requests
import re

# JULI Worker URL
JULI_SUB_URL = "https://smt-proxy.sufern001.workers.dev"
DD_FILE = "DD.m3u"

def fetch(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text

def extract_juli_strict(text):
    lines = text.splitlines()
    juli_lines = []
    capture = False

    for line in lines:
        # 只匹配 group-title="JULI" （大小写不敏感）
        if line.startswith("#EXTINF:") and re.search(r'group-title=["\']JULI["\']', line, re.IGNORECASE):
            capture = True
            # 替换为 HK
            line = re.sub(r'group-title=["\'].*?["\']', 'group-title="HK"', line)
            juli_lines.append(line)
            continue

        # URL 行，只有 capture=True 才抓
        if capture and line.strip() != "":
            juli_lines.append(line)
            capture = False

    return "\n".join(juli_lines)

def main():
    print("[+] Fetch JULI subscription")
    juli_raw = fetch(JULI_SUB_URL)
    juli_only = extract_juli_strict(juli_raw)

    with open(DD_FILE, "w", encoding="utf-8") as f:
        f.write(juli_only + "\n")

    print(f"[✓] Generated {DD_FILE} (strict JULI → HK)")

if __name__ == "__main__":
    main()
