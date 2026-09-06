import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from test_helpers import ROOT, initial, assessed, state, resource


def course():
    result = assessed()
    result["chapters"].append({"id": "c2", "title": "Mixed problems", "source_ids": [], "units": [],
                               "outcomes": [{"id": "o2", "description": "Explain unlike fractions",
                                             "status": "unassessed", "evidence_attempt_ids": [],
                                             "prerequisite_outcome_ids": ["o1"]}]})
    return result


class ReadinessTests(unittest.TestCase):
    def test_legacy_and_omitted_dependencies(self):
        self.assertEqual(state.readiness(assessed(), "c1")["readiness"], "ready")
        state.validate(initial())
        candidate = course()
        candidate["chapters"][1]["outcomes"][0]["prerequisite_outcome_ids"] = []
        self.assertEqual(state.readiness(candidate, "c2")["details"]["gaps"], [])

    def test_all_statuses_and_unchanged_input(self):
        for status, expected in (("unassessed", "not_ready"), ("needs-practice", "not_ready"),
                                 ("demonstrated-with-help", "not_ready"), ("demonstrated-independently", "ready")):
            with self.subTest(status=status):
                candidate = course()
                candidate["chapters"][0]["outcomes"][0]["status"] = status
                original = copy.deepcopy(candidate)
                report = state.readiness(candidate, "c2")
                self.assertEqual(report["readiness"], expected)
                self.assertEqual(candidate, original)
                if expected == "not_ready":
                    self.assertEqual(report["details"]["gaps"][0]["current_status"], status)
                    self.assertTrue(report["details"]["gaps"][0]["repair_suggestion"])

    def test_transitive_gap_even_when_immediate_prerequisite_independent(self):
        candidate = course()
        candidate["chapters"][0]["outcomes"][0]["prerequisite_outcome_ids"] = ["o0"]
        candidate["chapters"][0]["outcomes"].append({"id": "o0", "description": "Equal pieces",
                                                     "status": "unassessed", "evidence_attempt_ids": []})
        report = state.readiness(candidate, "c2")
        self.assertEqual(report["readiness"], "not_ready")
        self.assertEqual([g["outcome_id"] for g in report["details"]["gaps"]], ["o0"])
        self.assertEqual(report["details"]["outcomes"][0]["transitive_prerequisites"], ["o0", "o1"])

    def test_shared_prerequisites_are_reported_once(self):
        candidate = course()
        candidate["chapters"][0]["outcomes"][0]["status"] = "needs-practice"
        candidate["chapters"][1]["outcomes"].append(dict(candidate["chapters"][1]["outcomes"][0], id="o3"))
        self.assertEqual(len(state.readiness(candidate, "c2")["details"]["gaps"]), 1)

    def test_unknown_chapter(self):
        with self.assertRaisesRegex(ValueError, "unknown chapter"):
            state.readiness(course(), "missing")

    def test_invalid_dependencies(self):
        for value in (None, "o1", ["missing"], [4], [["o1"]], ["o1", "o1"]):
            with self.subTest(value=value):
                candidate = course()
                candidate["chapters"][1]["outcomes"][0]["prerequisite_outcome_ids"] = value
                with self.assertRaises(ValueError):
                    state.validate(candidate)

    def test_self_cycle_and_longer_cycle(self):
        candidate = course()
        candidate["chapters"][0]["outcomes"][0]["prerequisite_outcome_ids"] = ["o2"]
        with self.assertRaisesRegex(ValueError, r"cycle: o1 -> o2 -> o1"):
            state.readiness(candidate, "c2")
        candidate = course()
        candidate["chapters"][1]["outcomes"][0]["prerequisite_outcome_ids"] = ["o2"]
        with self.assertRaisesRegex(ValueError, r"cycle: o2 -> o2"):
            state.validate(candidate)

    def test_deep_graph_does_not_depend_on_python_recursion_limit(self):
        candidate = initial()
        outcomes = [{"id": f"o{i}", "description": f"Concept {i}", "status": "unassessed",
                     "evidence_attempt_ids": [], "prerequisite_outcome_ids": [f"o{i + 1}"] if i < 1100 else []}
                    for i in range(1101)]
        candidate["chapters"] = [{"id": "c1", "title": "Foundations", "units": [], "source_ids": [], "outcomes": outcomes[1:]},
                                 {"id": "c2", "title": "Target", "units": [], "source_ids": [], "outcomes": outcomes[:1]}]
        self.assertEqual(len(state.readiness(candidate, "c2")["details"]["gaps"]), 1100)

    def test_cli_reports_and_preserves_file_without_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            candidate = course()
            path.write_text(json.dumps(candidate), encoding="utf-8")
            before = path.read_bytes()
            script = str(ROOT / "scripts" / "session_state.py")
            for command in ("readiness", "repair"):
                result = subprocess.run([sys.executable, script, command, str(path), "--chapter", "c2"],
                                        capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["chapter_id"], "c2")
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(list(Path(directory).iterdir()), [path])
            candidate["chapters"][0]["outcomes"][0]["status"] = "needs-practice"
            path.write_text(json.dumps(candidate))
            result = subprocess.run([sys.executable, script, "readiness", str(path), "--chapter", "c2"],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(json.loads(result.stdout)["readiness"], "not_ready")
            candidate["chapters"][0]["outcomes"][0]["prerequisite_outcome_ids"] = ["o2"]
            path.write_text(json.dumps(candidate))
            result = subprocess.run([sys.executable, script, "readiness", str(path), "--chapter", "c2"],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("prerequisite cycle", result.stderr)


class RepairTests(unittest.TestCase):
    def test_no_gaps_no_questions(self):
        self.assertEqual(state.repair(course(), "c2", True)["gaps"], [])

    def test_drafts_target_owner_and_avoid_existing_ids(self):
        candidate = course()
        candidate["chapters"][0]["outcomes"][0]["status"] = "needs-practice"
        candidate["questions"].append(dict(candidate["questions"][0], id="repair-o1"))
        original = copy.deepcopy(candidate)
        report = state.repair(candidate, "c2", True)
        question = report["gaps"][0]["suggested_repair_question"]
        self.assertEqual(question["id"], "repair-o1-1")
        self.assertEqual(question["chapter_id"], "c1")
        self.assertEqual(question["outcome_ids"], ["o1"])
        self.assertEqual(question["kind"], "repair")
        self.assertIn("Add fractions", question["prompt"])
        self.assertEqual(candidate, original)
        candidate["questions"].append(question)
        candidate["attempts"].append({"id": "repair-attempt", "question_id": question["id"],
                                      "answer": "My explanation", "assistance": "hint",
                                      "feedback": "Guided practice", "kind": "repair"})
        state.validate(candidate)
        self.assertEqual(candidate["attempts"][0], original["attempts"][0])

    def test_without_generate_only_lists_relevant_recorded_gaps(self):
        candidate = course()
        candidate["chapters"][0]["outcomes"][0]["status"] = "needs-practice"
        candidate["chapters"][1]["outcomes"][0].update(status="needs-practice", evidence_attempt_ids=["a2"])
        candidate["questions"].append({"id": "q2", "chapter_id": "c2", "outcome_ids": ["o2"], "prompt": "Explain"})
        candidate["attempts"].append(dict(candidate["attempts"][0], id="a2", question_id="q2"))
        gaps = state.repair(candidate, "c2")["gaps"]
        self.assertEqual([g["outcome_id"] for g in gaps], ["o1", "o2"])
        self.assertTrue(all("suggested_repair_question" not in gap for gap in gaps))

    def test_generate_cli_does_not_persist_drafts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            candidate = course()
            candidate["chapters"][0]["outcomes"][0]["status"] = "needs-practice"
            path.write_text(json.dumps(candidate))
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "session_state.py"), "repair", str(path),
                                     "--chapter", "c2", "--generate"], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["gaps"][0]["suggested_repair_question"]["requires_agent_review"])
            self.assertEqual(path.read_bytes(), before)


class BlockExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_markdown_nesting_skipped_levels_siblings_and_reset(self):
        source = self.directory / "topic.md"
        source.write_text("Intro\n# A\n### Deep\nText\n## Sibling\nOther\n# B\nEnd", encoding="utf-8")
        result = resource.extract(source, "s1")
        blocks = result["extracted_blocks"]
        self.assertEqual([b["heading_path"] for b in blocks], [[], ["A"], ["A", "Deep"], ["A", "Deep"],
                                                                  ["A", "Sibling"], ["A", "Sibling"], ["B"], ["B"]])
        self.assertEqual(blocks[2]["heading_level"], 3)
        self.assertEqual(blocks[3]["line_range"], [4, 4])

    def test_code_fences_do_not_create_headings_and_keep_language(self):
        source = self.directory / "topic.md"
        source.write_text('# Python\n```python\n# comment\nvalue = "```"\n```\n~~~text\n## literal\n~~~\nAfter', encoding="utf-8")
        blocks = resource.extract(source, "s1")["extracted_blocks"]
        self.assertEqual([b["type"] for b in blocks], ["heading", "code_block", "code_block", "paragraph"])
        self.assertEqual(blocks[1]["code_language"], "python")
        self.assertEqual(blocks[1]["heading_path"], ["Python"])
        self.assertEqual(blocks[2]["line_range"], [6, 8])

    def test_unclosed_fence_is_flagged(self):
        source = self.directory / "topic.md"
        source.write_text("```\n# literal")
        block = resource.extract(source, "s1")["extracted_blocks"][0]
        self.assertEqual(block["type"], "code_block")
        self.assertEqual(block["extraction_status"], "low_confidence")

    def test_paragraphs_preserve_multiline_content_and_heading_hashes(self):
        source = self.directory / "topic.md"
        source.write_text("# C#\nFirst line\nsecond line\n\nNext paragraph\n## Nested ###\nExample")
        blocks = resource.extract(source, "s1")["extracted_blocks"]
        self.assertEqual(blocks[0]["content"], "C#")
        self.assertEqual(blocks[1]["content"], "First line\nsecond line")
        self.assertEqual(blocks[1]["line_range"], [2, 3])
        self.assertEqual(blocks[3]["content"], "Nested")

    def test_ids_metadata_and_legacy_records(self):
        source = self.directory / "topic.md"
        source.write_text("# A\nText", encoding="utf-8")
        result = resource.extract(source, "s1")
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["source_type"], "markdown")
        self.assertEqual(result["metadata"]["format_version"], "1.1")
        self.assertEqual(result["metadata"]["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(result["metadata"]["total_blocks"], 2)
        self.assertEqual([b["block_id"] for b in result["extracted_blocks"]], ["b1", "b2"])
        self.assertEqual(result["records"][0]["text"], "# A\nText")
        self.assertEqual(resource.extract(source, "s1")["extracted_blocks"], result["extracted_blocks"])

    def test_docx_style_names_inheritance_and_table_paths(self):
        source = self.directory / "topic.docx"
        styles = f'''<w:styles xmlns:w="{resource.W[1:-1]}">
        <w:style w:styleId="CustomOne"><w:name w:val="Heading 1"/></w:style>
        <w:style w:styleId="Deep"><w:name w:val="Heading 3"/></w:style>
        <w:style w:styleId="Inherited"><w:name w:val="My heading"/><w:basedOn w:val="Deep"/></w:style>
        <w:style w:styleId="Second"><w:name w:val="Heading 2"/></w:style>
        </w:styles>'''
        paragraphs = []
        for style, text in [(None, "Intro"), ("CustomOne", "A"), ("Inherited", "Deep section"),
                            (None, "Detail"), ("Second", "Sibling"), ("CustomOne", "B")]:
            prop = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
            paragraphs.append(f'<w:p>{prop}<w:r><w:t>{text}</w:t></w:r></w:p>')
        paragraphs.insert(4, '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Cell</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
        document = f'<w:document xmlns:w="{resource.W[1:-1]}"><w:body>{"".join(paragraphs)}</w:body></w:document>'
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("word/document.xml", document)
            archive.writestr("word/styles.xml", styles)
        blocks = resource.extract(source, "s1")["extracted_blocks"]
        self.assertEqual(blocks[0]["heading_path"], [])
        self.assertEqual(blocks[2]["style_name"], "My heading")
        self.assertEqual(blocks[2]["heading_level"], 3)
        self.assertEqual(blocks[3]["heading_path"], ["A", "Deep section"])
        self.assertEqual(blocks[4]["table_structure"], [["Cell"]])
        self.assertEqual(blocks[4]["heading_path"], ["A", "Deep section"])
        self.assertEqual(blocks[5]["heading_path"], ["A", "Sibling"])
        self.assertEqual(blocks[6]["heading_path"], ["B"])
        self.assertTrue(all("line_range" not in block for block in blocks))

    def test_plain_text_does_not_parse_markdown(self):
        source = self.directory / "topic.txt"
        source.write_text("# Not a heading\nText")
        block = resource.extract(source, "s1")["extracted_blocks"][0]
        self.assertEqual(block["type"], "paragraph")
        self.assertEqual(block["heading_path"], [])


if __name__ == "__main__":
    unittest.main()
