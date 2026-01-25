import xml.etree.ElementTree as ET
import re

def clean_xml(file_path):
    # 读取文件内容
    with open(file_path, "rb") as f:
        data = f.read()
    # 尝试转 utf-8 并去掉非法字符
    text = data.decode("utf-8", errors="ignore")
    # 去掉控制字符
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]", "", text)
    return text

tv = ET.Element("tv")

for f in ("pp.xml", "t.xml"):
    text = clean_xml(f)
    root = ET.fromstring(text)
    for child in root:
        tv.append(child)

ET.ElementTree(tv).write(
    "epg-all.xml",
    encoding="utf-8",
    xml_declaration=True
)

print("EPG merged successfully")
