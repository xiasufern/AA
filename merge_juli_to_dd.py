import requests
import base64
import re

JULI_SUB_URL = "https://smart.946985.filegear-sg.me/sub.php?user=tg_Thinkoo_bot"
BB_URL = "https://raw.githubusercontent.com/xiasufern/AA/main/BB.m3u"

OUTPUT_FILE = "DD.m3u"
KEYWORD = "JULI"
TARGET_GROUP = "HK"


def is_base64(s: str) -> bool:
    try:
        s = s.replace("\n", "").replace("\r", "")
        return base64.b64encode(base64.b64decode(s)) == s.encode()
    except Exception:
        return False


def fetch(url: str) -> str:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text.strip()


def decode_sub(content: str) -> str:
    if content.startswith("#EXTM3U"):
        return content
    if is_base64(content):
        return base64.b64decode(content).decode("utf-8", errors="ignore")
    return content


def extract_juli(content: str):
    lines = content.splitlines()
    result = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("#EXTINF") and KEYWORD.lower() in line.lower():
            if "group-title=" in line:
                line = re.sub(
                    r'group-title=".*?"',
                    f'group-title="{TARGET_GROUP}"',
                    line
                )
            else:
                line = line.replace(
                    "#EXTINF:-1",
                    f'#EXTINF:-1 group-title="{TARGET_GROUP}"'
                )

            result.append(line)

            if i + 1 < len(lines):
                result.append(lines[i + 1])

            i += 2
            continue

        i += 1

    return result


def main():
    print("[+] Fetch JULI subscription")
    juli_raw = fetch(JULI_SUB_URL)
    juli_content = decode_sub(juli_raw)

    print("[+] Extract JULI channels")
    juli_channels = extract_juli(juli_content)

    if not juli_channels:
        print("[-] No JULI channels found")
        return

    print("[+] Fetch BB.m3u")
    bb_content = fetch(BB_URL)

    merged = bb_content.rstrip() + "\n\n" + "\n".join(juli_channels) + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(merged)

    print(f"[✓] Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
