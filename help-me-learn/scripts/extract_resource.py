"""Extract local learning resources to JSON with source locators; no network access."""

import argparse
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


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
    if body is None:
        raise ValueError("DOCX has no main document body")
    records, heading = [], None
    for index, block in enumerate(body, 1):
        if block.tag == W + "p":
            text = paragraph_text(block)
            style = block.find(f"{W}pPr/{W}pStyle")
            if style is not None and re.match(r"heading\s*\d+", style.get(W + "val", ""), re.I):
                heading = text
            if text:
                records.append({"locator": {"body_block": index, "heading": heading, "kind": "paragraph"},
                                "text": text, "warnings": []})
        elif block.tag == W + "tbl":
            rows = []
            for row in block.findall(W + "tr"):
                rows.append(["\n".join(paragraph_text(p) for p in cell.findall(W + "p"))
                             for cell in row.findall(W + "tc")])
            records.append({"locator": {"body_block": index, "heading": heading, "kind": "table"},
                            "rows": rows, "text": "\n".join("\t".join(row) for row in rows),
                            "warnings": ["Merged cells and nested tables need source inspection."]})
    return records, ["Main-body paragraphs and tables only; images, headers, footers, comments, text boxes, and page layout are not extracted.",
                     "Custom or localized heading styles may not be recognized."]


def extract(path, source_id):
    path = Path(path).resolve()
    if not source_id.strip():
        raise ValueError("source-id must not be empty")
    if not path.is_file():
        raise ValueError(f"not a local file: {path}")
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md", ".markdown"):
        records, limitations = text_records(path)
    elif suffix == ".pdf":
        records, limitations = pdf_records(path)
    elif suffix == ".docx":
        records, limitations = docx_records(path)
    else:
        raise ValueError(f"unsupported format: {suffix or '(no extension)'}; use host tools or a readable extract")
    return {"schema_version": 1, "source_id": source_id, "title": path.name, "location": str(path),
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
