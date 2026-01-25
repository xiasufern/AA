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
    output = ["#EXTM3U"]

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF") and 'group-title="JULI"' in line:
            line = line.replace('group-title="JULI"', 'group-title="HK"')
            output.append(line)

            if i + 1 < len(lines):
                output.append(lines[i + 1].strip())

            i += 2
        else:
            i += 1

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output) + "\n")

    print(f"生成 EE.m3u，频道数：{(len(output)-1)//2}")

if __name__ == "__main__":
    main()
