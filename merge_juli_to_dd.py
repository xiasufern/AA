import requests
import re

# JULI Worker URL
JULI_SUB_URL = "https://smt-proxy.sufern001.workers.dev"
DD_FILE = "DD.m3u"

def fetch(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text

def extract_juli_only(text):
    lines = text.splitlines()
    juli_lines = []
    capture = False

    for line in lines:
        # 找到 #EXTINF 且 group-title="JULI" 的条目
        if line.startswith("#EXTINF:") and 'group-title="JULI"' in line:
            capture = True
            # 替换为 HK 分组
            line = re.sub(r'group-title=".*?"', 'group-title="HK"', line)
            juli_lines.append(line)
            continue

        # URL 行，capture=True 才抓
        if capture and line.strip() != "":
            juli_lines.append(line)
            capture = False

    return "\n".join(juli_lines)

def main():
    print("[+] Fetch JULI subscription")
    juli_raw = fetch(JULI_SUB_URL)
    juli_only = extract_juli_only(juli_raw)

    with open(DD_FILE, "w", encoding="utf-8") as f:
        f.write(juli_only + "\n")

    print(f"[✓] Generated {DD_FILE} (only JULI → HK)")

if __name__ == "__main__":
    main()
