import requests
import gzip
import shutil
import xml.etree.ElementTree as ET

EPG1 = "https://epg.112114.xyz/pp.xml"
EPG2 = "https://epg.946985.filegear-sg.me/t.xml.gz"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def download(url):
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.content

# 下载
pp_xml = download(EPG1)
t_gz = download(EPG2)

# 解压
with gzip.open(io := gzip.BytesIO(t_gz), "rb") as f:
    t_xml = f.read()

# 解析合并
tv = ET.Element("tv")

for data in (pp_xml, t_xml):
    root = ET.fromstring(data)
    for child in root:
        tv.append(child)

ET.ElementTree(tv).write(
    "epg-all.xml",
    encoding="utf-8",
    xml_declaration=True
)

print("EPG merged successfully")
