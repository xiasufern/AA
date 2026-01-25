import requests
import re

# JULI 订阅 Worker URL
JULI_SUB_URL = "https://smt-proxy.sufern001.workers.dev"
DD_FILE = "DD.m3u"

def fetch(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text

def extract_juli_channels(juli_text):
    lines = juli_text.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("#EXTINF:"):
            # 统一分组为 HK
            if "group-title=" not in line:
                line = line.replace("#EXTINF:", '#EXTINF:-1 group-title="HK",')
            else:
                line = re.sub(r'group-title=".*?"', 'group-title="HK"', line)
        new_lines.append(line)
    return "\n".join(new_lines)

def main():
    print("[+] Fetch JULI subscription")
    juli_raw = fetch(JULI_SUB_URL)
    juli_channels = extract_juli_channels(juli_raw)

    # 只保存 JULI 直播
    with open(DD_FILE, "w", encoding="utf-8") as f:
        f.write(juli_channels.strip() + "\n")

    print(f"[✓] Generated {DD_FILE} (only JULI)")

if __name__ == "__main__":
    main()
