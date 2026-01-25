import requests
import re
from datetime import datetime

# JULI Worker URL
JULI_SUB_URL = "https://smt-proxy.sufern001.workers.dev"
EE_FILE = "EE.m3u"   # 输出文件名

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
        return ""  # 返回空字符串，保证脚本不会报错

def extract_strict_juli(text):
    lines = text.splitlines()
    juli_lines = []
    capture = False

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")  # UTC 时间戳

    for line in lines:
        # 只抓 group-title="JULI" 的条目
        if line.startswith("#EXTINF:") and re.search(r'group-title=["\']JULI["\']', line, re.IGNORECASE):
            capture = True
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
    if not juli_raw.strip():
        print("⚠️ JULI source is empty, generating empty EE.m3u")
    juli_only = extract_strict_juli(juli_raw)

    # 覆盖写入 EE.m3u
    with open(EE_FILE, "w", encoding="utf-8") as f:
        f.write(juli_only + "\n")

    print(f"[✓] Generated {EE_FILE} (strict JULI → HK, overwrite)")

if __name__ == "__main__":
    main()
