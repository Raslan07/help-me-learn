"""Extract local learning resources to JSON with source locators; no network access."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def update_heading(stack, level, text):
    while stack and stack[-1][0] >= level:
        stack.pop()
    stack.append((level, text))
    return [heading for _, heading in stack]


def markdown_blocks(path):
    """Separate ATX headings, paragraphs and fenced code without changing legacy records."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    blocks, stack, buffer = [], [], []
    start, fence, language = 1, None, ""

    def flush(end, kind="paragraph", warnings=None):
        if not buffer:
            return
        block = {"type": kind, "content": "\n".join(buffer), "line_range": [start, end],
                 "heading_path": [heading for _, heading in stack],
                 "extraction_status": "low_confidence" if warnings else "success"}
        if kind == "code_block":
            block["code_language"] = language
        if warnings:
            block["warnings"] = warnings
        blocks.append(block)
        buffer.clear()

    for number, line in enumerate(lines, 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                # Include fences in content so line ranges refer to the exact extract.
                buffer.append(line)
                flush(number, "code_block")
                fence = None
            else:
                buffer.append(line)
            continue
        if marker and not (marker[1][0] == "`" and "`" in marker[2]):
            flush(number - 1)
            start, fence = number, marker[1]
            language = marker[2].strip().split()[0] if marker[2].strip() else ""
            buffer.append(line)
            continue
        match = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?)|[ \t]*)$", line)
        if match:
            flush(number - 1)
            heading = re.sub(r"[ \t]+#+[ \t]*$", "", match[2] or "").strip()
            heading_path = update_heading(stack, len(match[1]), heading)
            blocks.append({"type": "heading", "content": heading,
                           "heading_level": len(match[1]), "heading_path": heading_path,
                           "line_range": [number, number], "extraction_status": "success"})
        elif not line.strip():
            flush(number - 1)
        else:
            if not buffer:
                start = number
            buffer.append(line)
    flush(len(lines), "code_block" if fence else "paragraph",
          ["Unclosed fenced code block; inspect source."] if fence else None)
    return blocks


def text_records(path):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    markdown = path.suffix.lower() in (".md", ".markdown")
    records, buffer = [], []
    heading, start, fence = None, 1, None
    for number, line in enumerate(lines, 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line) if markdown else None
        match = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line) if markdown and fence is None else None
        if match and buffer:
            records.append({"locator": {"line_start": start, "line_end": number - 1, "heading": heading},
                            "text": "\n".join(buffer), "warnings": []})
            buffer, start = [], number
        if match:
            heading = match[2]
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not line[marker.end():].strip():
                fence = None
        buffer.append(line)
    if buffer:
        records.append({"locator": {"line_start": start, "line_end": len(lines), "heading": heading},
                        "text": "\n".join(buffer), "warnings": []})
    return records, ["Line ranges refer to the original file; Markdown heading detection is ATX-only."]


def pdf_records(path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF extraction needs optional dependency pypdf. Use a host PDF reader or install pypdf in an authorized environment.") from exc
    reader = PdfReader(path)
    if reader.is_encrypted and not reader.decrypt(""):
        raise ValueError("PDF is password protected; provide an accessible copy")
    labels = reader.page_labels
    records = []
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        warnings = []
        if len(text.strip()) < 40:
            warnings.append("little_extracted_text: inspect visually or with OCR; not necessarily blank or scanned")
        records.append({"locator": {"file_page": index + 1, "page_label": labels[index]},
                        "text": text, "warnings": warnings})
    return records, ["Text extraction does not inspect images or verify equations, layout, or reading order.",
                     "The low-text threshold is a heuristic, not a scan detector."]


def paragraph_text(element):
    parts = []
    def visit(node):
        if node.tag in (W + "drawing", W + "pict", W + "txbxContent", W + "del"):
            return
        if node.tag == W + "t":
            parts.append(node.text or "")
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            parts.append("\n")
        for child in node:
            visit(child)
    visit(element)
    return "".join(parts)


def docx_records(path):
    with zipfile.ZipFile(path) as archive:
        info = archive.getinfo("word/document.xml")
        if info.file_size > 50_000_000:
            raise ValueError("DOCX main document exceeds 50 MB extraction limit; use a smaller section")
        body = ET.fromstring(archive.read(info)).find(W + "body")
        styles = {}
        if "word/styles.xml" in archive.namelist():
            style_info = archive.getinfo("word/styles.xml")
            if style_info.file_size > 5_000_000:
                raise ValueError("DOCX styles exceed 5 MB extraction limit")
            style_root = ET.fromstring(archive.read(style_info))
            for style in style_root.findall(W + "style"):
                name = style.find(W + "name")
                based_on = style.find(W + "basedOn")
                outline = style.find(f"{W}pPr/{W}outlineLvl")
                styles[style.get(W + "styleId")] = {
                    "name": name.get(W + "val", "") if name is not None else "",
                    "parent": based_on.get(W + "val") if based_on is not None else None,
                    "outline": outline.get(W + "val") if outline is not None else None}
    if body is None:
        raise ValueError("DOCX has no main document body")
    records, heading, stack = [], None, []

    def heading_level(style_id, paragraph):
        direct = paragraph.find(f"{W}pPr/{W}outlineLvl")
        if direct is not None:
            raw = direct.get(W + "val", "")
            if raw.isdigit():
                return int(raw) + 1 if 0 <= int(raw) <= 8 else None
        visited = set()
        while style_id and style_id not in visited:
            visited.add(style_id)
            style = styles.get(style_id, {})
            raw = style.get("outline")
            if raw is not None and raw.isdigit():
                return int(raw) + 1 if 0 <= int(raw) <= 8 else None
            match = re.fullmatch(r"heading\s*([1-9])", style.get("name") or style_id, re.I)
            if match:
                return int(match[1])
            style_id = style.get("parent")
        return None

    for index, block in enumerate(body, 1):
        if block.tag == W + "p":
            text = paragraph_text(block)
            style = block.find(f"{W}pPr/{W}pStyle")
            style_id = style.get(W + "val", "") if style is not None else ""
            level = heading_level(style_id, block)
            if level is not None:
                heading = text
                update_heading(stack, level, text)
            if text:
                record = {"locator": {"body_block": index, "heading": heading, "kind": "paragraph"},
                          "text": text, "warnings": [], "heading_path": [title for _, title in stack],
                          "style_name": styles.get(style_id, {}).get("name", style_id)}
                if level is not None:
                    record["heading_level"] = level
                records.append(record)
        elif block.tag == W + "tbl":
            rows = []
            for row in block.findall(W + "tr"):
                rows.append(["\n".join(paragraph_text(p) for p in cell.findall(W + "p"))
                             for cell in row.findall(W + "tc")])
            records.append({"locator": {"body_block": index, "heading": heading, "kind": "table"},
                            "rows": rows, "text": "\n".join("\t".join(row) for row in rows),
                            "heading_path": [title for _, title in stack],
                            "warnings": ["Merged cells and nested tables need source inspection."]})
    return records, ["Main-body paragraphs and tables only; images, headers, footers, comments, text boxes, and page layout are not extracted.",
                     "Heading names, outline levels and inherited styles are read from OOXML; styles without heading metadata may not be recognized."]


def structured_blocks(records, source_type):
    result = []
    for record in records:
        locator = record["locator"]
        kind = "page" if source_type == "pdf" else locator.get("kind", "paragraph")
        block = {"type": "heading" if "heading_level" in record else kind,
                 "content": record["text"],
                 "extraction_status": "low_confidence" if record["warnings"] else "success"}
        if source_type == "pdf":
            block.update(file_page=locator["file_page"], printed_page=locator["page_label"])
        elif source_type == "docx":
            block.update(body_block=locator["body_block"], heading_path=record["heading_path"])
            for key in ("heading_level", "style_name"):
                if key in record:
                    block[key] = record[key]
            if "rows" in record:
                block["table_structure"] = record["rows"]
        else:
            block.update(line_range=[locator["line_start"], locator["line_end"]], heading_path=[])
        if record["warnings"]:
            block["warnings"] = record["warnings"]
        result.append(block)
    return result


def extract(path, source_id):
    path = Path(path).resolve()
    if not source_id.strip():
        raise ValueError("source-id must not be empty")
    if not path.is_file():
        raise ValueError(f"not a local file: {path}")
    suffix = path.suffix.lower()
    before = path.stat()
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    if suffix in (".txt", ".md", ".markdown"):
        records, limitations = text_records(path)
    elif suffix == ".pdf":
        records, limitations = pdf_records(path)
    elif suffix == ".docx":
        records, limitations = docx_records(path)
    else:
        raise ValueError(f"unsupported format: {suffix or '(no extension)'}; use host tools or a readable extract")
    source_type = {".txt": "text", ".md": "markdown", ".markdown": "markdown",
                   ".pdf": "pdf", ".docx": "docx"}[suffix]
    blocks = markdown_blocks(path) if source_type == "markdown" else structured_blocks(records, source_type)
    after = path.stat()
    if (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size):
        raise ValueError("Source changed during extraction; retry against a stable copy")
    for index, block in enumerate(blocks, 1):
        block["block_id"] = f"b{index}"
    return {"schema_version": 1, "source_id": source_id, "title": path.name, "location": str(path),
            "source_type": source_type, "extracted_blocks": blocks,
            "metadata": {"format_version": "1.1", "total_blocks": len(blocks),
                         "extraction_date": datetime.now(timezone.utc).date().isoformat(),
                         "python_version": platform.python_version(), "source_sha256": digest},
            "status": "extracted-not-reviewed", "limitations": limitations,
            "warnings": [] if records else ["No text records extracted; inspect source before proceeding."],
            "records": records}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--source-id", required=True)
    args = parser.parse_args()
    try:
        result = extract(args.path, args.source_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        # Optional parsers have different exception hierarchies; CLI errors must stay readable.
        print(f"Extraction error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
