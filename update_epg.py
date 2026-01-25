import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def clean_xml_file(filename):
    # 读取文件
    with open(filename, "rb") as f:
        data = f.read()
    # 忽略非法字符
    text = data.decode("utf-8", errors="ignore")
    # 用 BeautifulSoup 修复不规范 XML
    soup = BeautifulSoup(text, "xml")
    return soup.prettify()

tv = ET.Element("tv")

for f in ("pp.xml", "t.xml"):
    clean_text = clean_xml_file(f)
    root = ET.fromstring(clean_text)
    for child in root:
        tv.append(child)

ET.ElementTree(tv).write(
    "epg-all.xml",
    encoding="utf-8",
    xml_declaration=True
)

print("EPG merged successfully")
