"""Read the locally supplied DOCX without executing macros or extracting files."""
import hashlib
import re
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile


NAMESPACES = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def read_document(path):
    path = Path(path)
    with ZipFile(path) as archive:
        info = archive.getinfo("word/document.xml")
        if info.file_size > 5_000_000:
            raise ValueError("The source document is unexpectedly large.")
        body = ElementTree.fromstring(archive.read(info)).find("w:body", NAMESPACES)
        if body is None:
            raise ValueError("The source document has no body.")
        blocks = []
        for element in body:
            if element.tag.endswith("}p"):
                text = "".join(part.text or "" for part in element.findall(".//w:t", NAMESPACES)).strip()
                if text:
                    blocks.append({"type": "paragraph", "text": text})
            elif element.tag.endswith("}tbl"):
                rows = [["".join(part.text or "" for part in cell.findall(".//w:t", NAMESPACES)).strip()
                         for cell in row.findall("w:tc", NAMESPACES)]
                        for row in element.findall("w:tr", NAMESPACES)]
                if rows:
                    blocks.append({"type": "table", "headers": rows[0], "rows": rows[1:]})
    sections = {"introduction": []}
    current = "introduction"
    for block in blocks:
        heading = re.match(r"^(1\.[1-8])\.\s", block.get("text", ""))
        if heading:
            current = heading.group(1)
            sections[current] = []
        sections[current].append(block)
    if set(sections) != {"introduction", *(f"1.{number}" for number in range(1, 9))}:
        raise ValueError("Expected the supplied Chapter 1 sections 1.1–1.8.")
    return {"source_name": path.name, "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "blocks": blocks, "sections": sections,
            "tables": [block for block in blocks if block["type"] == "table"]}


def plain_text(blocks):
    """Complete readable fallback; tables retain their original cells and order."""
    return "\n\n".join(block["text"] if block["type"] == "paragraph" else
                        "\n".join(" | ".join(row) for row in [block["headers"], *block["rows"]])
                        for block in blocks)
