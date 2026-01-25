import gzip
import xml.etree.ElementTree as ET

tv = ET.Element("tv")

for f in ("pp.xml", "t.xml"):
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
