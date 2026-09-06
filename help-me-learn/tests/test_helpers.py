import builtins
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import session_state as state
import extract_resource as resource


def initial():
    return state.read_state(ROOT / "assets" / "session-state.json")


def assessed():
    result = initial()
    result["topic"] = "Fractions"
    result["chapters"] = [{"id": "c1", "title": "Addition", "source_ids": [],
                           "units": [{"id": "u1", "title": "Equal pieces"}],
                           "outcomes": [{"id": "o1", "description": "Add fractions",
                                         "status": "demonstrated-independently", "evidence_attempt_ids": ["a1"]}]}]
    result["questions"] = [{"id": "q1", "chapter_id": "c1", "outcome_ids": ["o1"], "prompt": "1/2 + 1/3?"}]
    result["attempts"] = [{"id": "a1", "question_id": "q1", "answer": "5/6 using sixths", "assistance": "none",
                           "feedback": "Correct: 3/6 + 2/6 = 5/6", "kind": "chapter-check"}]
    result["position"] = {"chapter_id": "c1", "unit_id": "u1", "question_id": "q1", "phase": "review"}
    return result


class StateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "state.json"

    def test_unicode_roundtrip_and_revision(self):
        original = initial()
        original["topic"] = "كسور"
        state.save_state(self.path, original, initialize=True)
        self.assertEqual(state.read_state(self.path), original)
        candidate = state.read_state(self.path)
        candidate["next_action"] = "Try one example"
        updated = state.save_state(self.path, candidate)
        self.assertEqual(updated["revision"], 1)
        self.assertEqual(state.read_state(self.path)["topic"], "كسور")

    def test_stale_update_and_reinitialization_preserve_file(self):
        state.save_state(self.path, initial(), initialize=True)
        state.save_state(self.path, initial())
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "stale"):
            state.save_state(self.path, initial())
        with self.assertRaisesRegex(ValueError, "already exists"):
            state.save_state(self.path, initial(), initialize=True)
        self.assertEqual(before, self.path.read_bytes())

    def test_interrupted_replace_preserves_original_and_cleans_temp(self):
        state.save_state(self.path, initial(), initialize=True)
        before = self.path.read_bytes()
        with patch.object(state.os, "replace", side_effect=OSError("simulated write failure")):
            with self.assertRaises(OSError):
                state.save_state(self.path, initial())
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_existing_lock_rejects_write(self):
        lock = self.path.with_name("state.json.lock")
        lock.write_text("")
        with self.assertRaises(FileExistsError):
            state.save_state(self.path, initial(), initialize=True)
        self.assertTrue(lock.exists())
        self.assertFalse(self.path.exists())

    def test_invalid_evidence_and_position_rejected(self):
        state.validate(assessed())
        for mutate in (
            lambda s: s["attempts"][0].update(assistance="hint"),
            lambda s: s["position"].update(unit_id="missing"),
            lambda s: s["chapters"][0]["outcomes"][0].update(evidence_attempt_ids=[]),
            lambda s: s.update(schema_version=True),
            lambda s: s["questions"][0].update(outcome_ids=["missing"]),
        ):
            candidate = assessed()
            mutate(candidate)
            with self.assertRaises(ValueError):
                state.validate(candidate)

    def test_history_is_preserved_but_new_attempts_can_be_appended(self):
        state.save_state(self.path, assessed(), initialize=True)
        bad = assessed()
        bad["attempts"][0]["answer"] = "changed"
        with self.assertRaisesRegex(ValueError, "attempts cannot"):
            state.save_state(self.path, bad)
        bad = assessed()
        bad["questions"][0]["prompt"] = "different problem"
        with self.assertRaisesRegex(ValueError, "questions with attempts"):
            state.save_state(self.path, bad)
        candidate = assessed()
        attempt = dict(candidate["attempts"][0], id="a2", kind="delayed-retrieval", date="2026-09-06")
        candidate["attempts"].append(attempt)
        saved = state.save_state(self.path, candidate)
        self.assertEqual(len(saved["attempts"]), 2)

    def test_duplicate_json_keys_and_nonfinite_numbers_rejected(self):
        for content in ('{"revision":0,"revision":1}', '{"revision":NaN}'):
            self.path.write_text(content)
            with self.assertRaises(ValueError):
                state.read_state(self.path)

    def test_pending_hint_survives_resume(self):
        candidate = assessed()
        candidate["position"].update(phase="paused", assistance="hint", hints=["Use equal-sized pieces."])
        state.save_state(self.path, candidate, initialize=True)
        resumed = state.read_state(self.path)
        self.assertEqual(resumed["position"]["question_id"], "q1")
        self.assertEqual(resumed["position"]["assistance"], "hint")
        self.assertEqual(resumed["position"]["hints"], ["Use equal-sized pieces."])

    def test_cli_lifecycle_and_error(self):
        script = ROOT / "scripts" / "session_state.py"
        for args in (["init", str(self.path), "--topic", "Fractions"], ["show", str(self.path)], ["validate", str(self.path)]):
            completed = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsInstance(json.loads(completed.stdout), dict)
        candidate = self.path.with_name("candidate.json")
        candidate.write_text(json.dumps(state.read_state(self.path)))
        completed = subprocess.run([sys.executable, str(script), "update", str(self.path), "--from", str(candidate)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        candidate.write_text("{}")
        completed = subprocess.run([sys.executable, str(script), "update", str(self.path), "--from", str(candidate)], capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("State error:", completed.stderr)
        self.assertEqual(state.read_state(self.path)["revision"], 1)


class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_markdown_locators_unicode_and_fenced_code(self):
        source = self.directory / "notes.md"
        source.write_text("Intro\n# Fractions\nكسور\n```python\n# not a heading\n```\n## Add\nExample", encoding="utf-8")
        result = resource.extract(source, "s1")
        self.assertEqual(len(result["records"]), 3)
        middle = result["records"][1]
        self.assertEqual(middle["locator"], {"line_start": 2, "line_end": 6, "heading": "Fractions"})
        self.assertIn("كسور", middle["text"])
        self.assertEqual(result["status"], "extracted-not-reviewed")

    def test_plain_text_and_empty_file(self):
        source = self.directory / "notes.txt"
        source.write_text("# literal\nsecond")
        result = resource.extract(source, "s1")
        self.assertIsNone(result["records"][0]["locator"]["heading"])
        source.write_text("")
        self.assertTrue(resource.extract(source, "s1")["warnings"])

    def test_docx_paragraph_table_order_and_heading(self):
        source = self.directory / "sample.docx"
        xml = '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
        <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Addition</w:t></w:r></w:p>
        <w:tbl><w:tr><w:tc><w:p><w:r><w:t>1/2</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>3/6</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
        <w:p><w:r><w:t>Equal pieces</w:t><w:tab/><w:t>matter</w:t><w:drawing><w:t>ignored image text</w:t></w:drawing></w:r></w:p>
        </w:body></w:document>'''
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("word/document.xml", xml)
        result = resource.extract(source, "s2")
        self.assertEqual([r["locator"]["kind"] for r in result["records"]], ["paragraph", "table", "paragraph"])
        self.assertEqual(result["records"][1]["rows"], [["1/2", "3/6"]])
        self.assertEqual(result["records"][2]["text"], "Equal pieces\tmatter")
        self.assertEqual(result["records"][2]["locator"]["heading"], "Addition")

    def test_missing_pdf_dependency_message(self):
        source = self.directory / "sample.pdf"
        source.write_bytes(b"dummy")
        original = builtins.__import__
        def without_pdf(name, *args, **kwargs):
            if name == "pypdf":
                raise ImportError("simulated missing dependency")
            return original(name, *args, **kwargs)
        with patch("builtins.__import__", side_effect=without_pdf):
            with self.assertRaisesRegex(ValueError, "optional dependency pypdf"):
                resource.extract(source, "s1")

    @unittest.skipUnless(importlib.util.find_spec("pypdf"), "optional pypdf not installed")
    def test_pdf_page_boundaries_labels_and_low_text(self):
        from pypdf import PdfWriter
        from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
        writer = PdfWriter()
        page = writer.add_blank_page(width=300, height=300)
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
        stream = DecodedStreamObject()
        stream.set_data(b"BT /F1 12 Tf 10 100 Td (Fractions use equal sized pieces to represent part of a whole.) Tj ET")
        page[NameObject("/Contents")] = writer._add_object(stream)
        writer.add_blank_page(width=300, height=300)
        writer.set_page_label(0, 1, prefix="Intro-")
        source = self.directory / "sample.pdf"
        writer.write(source)
        result = resource.extract(source, "s3")
        self.assertEqual([r["locator"]["file_page"] for r in result["records"]], [1, 2])
        self.assertTrue(result["records"][0]["locator"]["page_label"].startswith("Intro-"))
        self.assertIn("Fractions", result["records"][0]["text"])
        self.assertFalse(result["records"][0]["warnings"])
        self.assertIn("little_extracted_text", result["records"][1]["warnings"][0])
        blocks = result["extracted_blocks"]
        self.assertEqual([b["type"] for b in blocks], ["page", "page"])
        self.assertEqual(blocks[0]["file_page"], 1)
        self.assertEqual(blocks[0]["printed_page"], result["records"][0]["locator"]["page_label"])
        self.assertEqual(blocks[1]["extraction_status"], "low_confidence")
        self.assertEqual(blocks[1]["content"], "")
        self.assertNotIn("line_range", blocks[1])

    def test_unsupported_missing_and_malformed_input(self):
        with self.assertRaisesRegex(ValueError, "not a local file"):
            resource.extract(self.directory / "absent.md", "s1")
        source = self.directory / "chart.png"
        source.write_bytes(b"image")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            resource.extract(source, "s1")
        source = self.directory / "bad.docx"
        source.write_bytes(b"not a zip")
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_resource.py"), str(source), "--source-id", "s1"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Extraction error:", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_extraction_cli_json(self):
        source = self.directory / "notes.txt"
        source.write_text("مثال", encoding="utf-8")
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_resource.py"), str(source), "--source-id", "s1"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["records"][0]["text"], "مثال")


if __name__ == "__main__":
    unittest.main()
