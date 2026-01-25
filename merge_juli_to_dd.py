import requests
import os

# 你的 Workers URL
JULI_SUB_URL = "https://smt-proxy.sufern001.workers.dev"

# BB.m3u 仓库原文件
BB_URL = "https://raw.githubusercontent.com/xiasufern/AA/main/BB.m3u"

def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://google.com"
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text

def extract_juli_channels(juli_text):
    lines = juli_text.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("#EXTINF:"):
            line = line.replace('group-title=""', 'group-title="HK"')
        new_lines.append(line)
    return "\n".join(new_lines)

def main():
    print("[+] Fetch JULI subscription")
    juli_raw = fetch(JULI_SUB_URL)
    juli_content = extract_juli_channels(juli_raw)

    print("[+] Fetch BB.m3u")
    bb_raw = fetch(BB_URL)

    merged_content = bb_raw + "\n" + juli_content

    # 确保在当前目录生成 DD.m3u
    dd_path = os.path.join(os.getcwd(), "DD.m3u")
    with open(dd_path, "w", encoding="utf-8") as f:
        f.write(merged_content)

    print("[✓] Generated DD.m3u at:", dd_path)

if __name__ == "__main__":
    main()
