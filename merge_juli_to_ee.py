import requests

SOURCE_URL = "https://smt-proxy.sufern001.workers.dev/"
OUT_FILE = "EE.m3u"

def main():
    r = requests.get(
        SOURCE_URL,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        }
    )
    r.raise_for_status()
    text = r.text

    lines = text.splitlines()
    out = ["#EXTM3U"]

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 只要 JULI
        if line.startswith("#EXTINF") and 'group-title="JULI"' in line:
            # 改分组为 HK
            line = line.replace('group-title="JULI"', 'group-title="HK"')
            out.append(line)

            # 下一行一定是播放地址
            if i + 1 < len(lines):
                out.append(lines[i + 1].strip())
            i += 2
        else:
            i += 1

    # 覆盖写入
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    print(f"[OK] 写入 {OUT_FILE}，频道数：{(len(out)-1)//2}")

if __name__ == "__main__":
    main()
