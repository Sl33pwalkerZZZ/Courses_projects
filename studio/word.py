"""Bounded DOCX parsing without extraction, HTML, macros or external requests."""
import hashlib
import io
import re
from pathlib import PurePosixPath
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from courses.management.first_course_document import plain_text

MAX_UPLOAD = 10 * 1024 * 1024
MAX_XML = 5 * 1024 * 1024
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def xml(data):
    # DOCX XML is normally UTF-8. Reject NUL-bearing UTF-16/32 encodings so
    # alternate byte encodings cannot bypass the explicit entity/DTD filter.
    if len(data) > MAX_XML or b"\x00" in data or b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("Unsafe or oversized Word XML.")
    return ET.fromstring(data)


def parse_docx(data, filename):
    """Return an editable proposal only. This function never writes files or rows."""
    if not isinstance(data, bytes) or not data or len(data) > MAX_UPLOAD:
        raise ValueError("Upload a non-empty DOCX file of at most 10 MB.")
    if not isinstance(filename, str) or not filename.lower().endswith(".docx"):
        raise ValueError("Only DOCX documents are supported.")
    warnings = ["Formatting, embedded images, comments and tracked-change metadata are not imported. Review the proposed mapping before confirming."]
    try:
        with ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 2000 or sum(info.file_size for info in entries) > 30 * 1024 * 1024:
                raise ValueError("The expanded document exceeds the upload limit.")
            names = [info.filename for info in entries]
            if len(set(names)) != len(names):
                raise ValueError("Duplicate archive entries are not supported.")
            for info in entries:
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in info.filename or info.flag_bits & 1:
                    raise ValueError("Unsafe or encrypted document archive.")
                if info.filename.lower().endswith(("vbaproject.bin", ".exe", ".dll")):
                    raise ValueError("Executable or macro content is not supported.")
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ValueError("This file is not a Word DOCX document.")
            def read_xml(name):
                if archive.getinfo(name).file_size > MAX_XML:
                    raise ValueError("Word XML exceeds the parsing limit.")
                return xml(archive.read(name))
            content_types = read_xml("[Content_Types].xml")
            if any("macroenabled" in item.attrib.get("ContentType", "").lower() for item in content_types):
                raise ValueError("Macro-enabled documents are not supported.")
            links = {}
            rels = "word/_rels/document.xml.rels"
            if rels in names:
                for relationship in read_xml(rels):
                    target = relationship.attrib.get("Target", "")
                    if relationship.attrib.get("Type", "").endswith("/hyperlink"):
                        if re.match(r"^https?://[^\s<>]+$", target, re.I) and len(target) <= 2000:
                            links[relationship.attrib.get("Id")] = target
                        else:
                            warnings.append("An unsupported link was omitted; only HTTP(S) references are retained.")
            heading_styles = {}
            if "word/styles.xml" in names:
                for style in read_xml("word/styles.xml").findall("w:style", NS):
                    name = style.find("w:name", NS)
                    label = name.attrib.get(f"{{{NS['w']}}}val", "") if name is not None else ""
                    match = re.search(r"(?:heading|заголовок)\s*([1-6])", label, re.I)
                    if match:
                        heading_styles[style.attrib.get(f"{{{NS['w']}}}styleId")] = int(match.group(1))
            document = read_xml("word/document.xml")
            body = document.find("w:body", NS)
            if body is None:
                raise ValueError("The document has no readable body.")
            def text(element):
                result = "".join("\t" if node.tag == f"{{{NS['w']}}}tab" else "\n" if node.tag == f"{{{NS['w']}}}br" else node.text or ""
                                 for node in element.iter() if node.tag in {f"{{{NS['w']}}}t", f"{{{NS['w']}}}tab", f"{{{NS['w']}}}br"}).strip()
                for link in element.findall(".//w:hyperlink", NS):
                    url = links.get(link.attrib.get(f"{{{NS['r']}}}id"))
                    if url and url not in result:
                        result += f" ({url})"
                return result
            blocks = []
            for element in body:
                if element.tag == f"{{{NS['w']}}}p":
                    value = text(element)
                    if not value:
                        continue
                    if len(value) > 100000:
                        raise ValueError("A paragraph exceeds the content limit.")
                    style = element.find("w:pPr/w:pStyle", NS)
                    style_id = style.attrib.get(f"{{{NS['w']}}}val", "") if style is not None else ""
                    level = heading_styles.get(style_id)
                    match = re.search(r"(?:heading|заголовок)\s*([1-6])", style_id, re.I)
                    if level is None and match:
                        level = int(match.group(1))
                    if level is None and re.match(r"^\d+(?:\.\d+){0,2}[.)]?\s+\S", value) and len(value) < 255:
                        level = 2
                    block = {"type": "heading" if level else "paragraph", "text": value}
                    if level:
                        block["level"] = level
                    blocks.append(block)
                elif element.tag == f"{{{NS['w']}}}tbl":
                    rows = [[text(cell) for cell in row.findall("w:tc", NS)] for row in element.findall("w:tr", NS)]
                    if len(rows) > 200 or any(len(row) > 30 or any(len(cell) > 20000 for cell in row) for row in rows):
                        raise ValueError("A table exceeds the supported size.")
                    if rows:
                        blocks.append({"type": "table", "headers": rows[0], "rows": rows[1:]})
                if len(blocks) > 2000:
                    raise ValueError("The document contains too many content blocks.")
            if document.findall(".//w:drawing", NS) or any(name.startswith("word/media/") for name in names):
                warnings.append("Embedded illustrations were not extracted. Upload reviewed images separately using protected lesson assets.")
            if document.findall(".//w:ins", NS) or document.findall(".//w:del", NS):
                warnings.append("Tracked changes are present. Review all imported text carefully.")
    except (BadZipFile, KeyError, ET.ParseError, RuntimeError, NotImplementedError) as error:
        raise ValueError("The DOCX file is damaged or unsupported.") from error
    if not blocks:
        raise ValueError("The document has no readable paragraphs or tables.")
    if sum(len(str(block)) for block in blocks) > 1_000_000:
        raise ValueError("The extracted course text exceeds the content limit.")
    title = next((block["text"] for block in blocks if block["type"] == "heading"), PurePosixPath(filename.replace("\\", "/")).stem)[:255]
    lessons, current, introduction = [], None, []
    for block in blocks:
        if block["type"] == "heading" and block["level"] <= 2:
            if len(lessons) >= 100:
                raise ValueError("The proposed course exceeds 100 lessons; split the source document.")
            current = {"title": block["text"][:255], "blocks": introduction + [block]}
            introduction = []
            lessons.append(current)
        elif current is None:
            introduction.append(block)
        else:
            current["blocks"].append(block)
    if not lessons:
        lessons = [{"title": title, "blocks": blocks}]
    for lesson in lessons:
        lesson["text_content"] = plain_text([{**block, "type": "paragraph"} if block["type"] == "heading" else block for block in lesson["blocks"]])
    return {"source_name": PurePosixPath(filename.replace("\\", "/")).name[:255],
            "source_sha256": hashlib.sha256(data).hexdigest(), "title": title,
            "blocks": blocks, "lessons": lessons, "warnings": list(dict.fromkeys(warnings))}
