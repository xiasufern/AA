import gzip
import xml.etree.ElementTree as ET

tv = ET.Element("tv")

for f in ("pp.xml", "t.xml"):
    # 如果是 gzip 文件也可以用下面解压方法
    if f.endswith(".gz"):
        with gzip.open(f, "rb") as gz:
            tree = ET.parse(gz)
            root = tree.getroot()
            for child in root:
                tv.append(child)
    else:
        tree = ET.parse(f)
        root = tree.getroot()
        for child in root:
            tv.append(child)

ET.ElementTree(tv).write(
    "epg-all.xml",
    encoding="utf-8",
    xml_declaration=True
)

print("EPG merged")
