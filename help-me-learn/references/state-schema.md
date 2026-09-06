# State and helper commands

Use the agent's normal file tools if Python is absent. Follow the same schema and preserve prior attempts. With no writable workspace, use the [resume template](../assets/resume.md) in the conversation. State may contain learner answers: keep it local and out of the distributed skill.

## Commands

Replace `<skill>` and `<learner>` with actual paths; quote paths containing spaces. The destination parent directory must already exist. Python 3.10+ is the intended runtime; tests were run on the version recorded in the validation report.

```text
python "<skill>/scripts/session_state.py" init "<learner>/state.json" --topic "Fractions" --goal "Add unlike fractions"
python "<skill>/scripts/session_state.py" show "<learner>/state.json"
python "<skill>/scripts/session_state.py" validate "<learner>/state.json"
python "<skill>/scripts/session_state.py" update "<learner>/state.json" --from "<learner>/candidate.json"
python "<skill>/scripts/session_state.py" readiness "<learner>/state.json" --chapter ch2
python "<skill>/scripts/session_state.py" repair "<learner>/state.json" --chapter ch2 --generate
```

For an update, read current state, copy it to a separate candidate file, edit that copy, and keep its current `revision`. The helper validates the entire replacement and increments the revision after a successful save. Omitted fields are not merged. Never edit the destination first and then call update: that defeats protection of the prior version.

The helper uses a sibling temporary file and atomic replacement, plus an exclusive sibling `.lock` file. A rejected update or failed replacement preserves the existing file. A stale revision is rejected. Other writers must also use the helper for locking to coordinate them. This is not a backup/version-control system or a guarantee against storage-device failure.

If a process crashes and leaves a lock, verify no writer is active before removing only that lock. Preserve a malformed state file for inspection; do not silently replace it with a blank session. Unknown schema versions require explicit migration. The helper never creates a missing parent directory or installs dependencies.

## Schema version 1

The [starter JSON](../assets/session-state.json) is valid before a topic is selected. Required fields:

| Field | Meaning |
| --- | --- |
| `schema_version`, `revision` | Version `1`; nonnegative integer revision, initially `0`. |
| `topic`, `goal`, `language` | Strings; empty until known. |
| `position` | `chapter_id`, `unit_id`, `question_id` are valid IDs or null; `phase` is intake, learning, assessment, review, paused, or complete. |
| `sources` | Records with `id`, `title`, `location`, `status`, `locators` (strings), and `limitations` (string). Status: listed, partial, read, unavailable. |
| `chapters` | Records with `id`, `title`, `source_ids`, `units`, and `outcomes`. Units have `id` and `title`. |
| `questions` | Records with `id`, `chapter_id`, `outcome_ids`, and `prompt`. Keep unrevealed answers out of learner-facing output. |
| `attempts` | Append-only records with `id`, `question_id`, `answer`, `assistance`, `feedback`, and `kind`. |
| `preferences` | Object of string values, such as `{"question_presentation": "one-at-a-time"}`. Store learner-stated preferences, not diagnoses. |
| `next_action` | One concrete action useful after interruption. |

Outcome records require `id`, `description`, `status`, and `evidence_attempt_ids`. Optionally include `prerequisite_outcome_ids` to model concept dependencies. Omit it or use `[]` when none are declared; existing version 1 files remain valid. IDs must be globally unique for outcomes and unique within other record collections; unit IDs need only be unique within a chapter. Question outcomes must belong to their chapter. Evidence must reference an attempt that actually targets that outcome.

Outcome statuses: `unassessed`, `needs-practice`, `demonstrated-with-help`, `demonstrated-independently`. All assessed statuses need evidence; independent status requires at least one unassisted attempt. The helper checks structure and links, not answer correctness. The agent must judge whether evidence supports the label.

Assistance: `none`, `hint`, `solution`. Attempt kinds: `practice`, `chapter-check`, `retry`, `delayed-retrieval`, and the additive `repair` kind. Older helpers do not understand `repair`; use the updated helper for files containing it. Delayed retrieval also requires `date` as an ISO date, for example `2026-09-06`. Other attempts may include a date too. Store hints and criteria as optional additional fields when needed. Additional JSON fields are preserved but not validated beyond core schema requirements.

Save a submitted answer immediately with empty feedback if review is pending. Because attempts are immutable through the helper, append a reviewed record with a new ID, the same answer and assistance, and optional `supersedes_attempt_id` referencing the pending record. Point outcome evidence to the reviewed record. Use the same approach to correct mistaken feedback; preserve the history and do not count superseded records as separate successes.

While awaiting an answer, keep assistance already given in `position.assistance` and the hint texts in `position.hints`. Copy that assistance into the submitted attempt, then reset these position fields when moving to a new question. This prevents a pause from turning a hinted answer into apparently independent evidence.

Questions with attempts cannot be changed through updates. If the key or prompt was flawed, create a corrected question with a new ID and record the correction. Make fresh retry questions distinct from the original.

`position.phase: complete` means the planned journey ended, not that all outcomes were mastered. Leave skipped outcomes unassessed. Save a new topic in a new state file.

## Prerequisites and readiness

An outcome may declare dependencies on outcomes in the same or another chapter:

```json
{
  "id": "oc2",
  "description": "Add fractions with unlike denominators",
  "status": "unassessed",
  "evidence_attempt_ids": [],
  "prerequisite_outcome_ids": ["oc0", "oc1"]
}
```

`oc0` and `oc1` must exist. Duplicate references, unknown IDs, self-dependencies, and cycles are validation errors. Cycles report the path instead of causing an infinite traversal. The optional field is validated whenever present; it is not free-form extension data.

`readiness` examines **all transitive prerequisites** of the target chapter's outcomes. Every required outcome must be `demonstrated-independently` for `ready`. `unassessed`, `needs-practice`, and `demonstrated-with-help` all produce `not_ready`, with each gap listed once, dependencies first. Independent evidence on an immediate prerequisite does not hide a gap in its own prerequisites.

Readiness describes recorded prerequisite evidence, not permission to learn. Offer focused repair; let the learner proceed or work statelessly if they choose. A chapter with no declared prerequisites is `ready`, which does not mean its own outcomes are mastered. Same-chapter prerequisite chains can make a whole chapter `not_ready` while its first outcome is teachable; teach in dependency order.

Both results have the same shape; `details.gaps` is empty for `ready`:

```json
{
  "chapter_id": "ch2",
  "chapter_title": "Add unlike fractions",
  "readiness": "not_ready",
  "details": {
    "outcomes": [{
      "id": "oc2",
      "description": "Add fractions with unlike denominators",
      "prerequisites": ["oc1"],
      "status": {"oc1": "needs-practice"},
      "transitive_prerequisites": ["oc1"]
    }],
    "gaps": [{
      "outcome_id": "oc1",
      "chapter_id": "ch1",
      "description": "Identify numerator and denominator",
      "current_status": "needs-practice",
      "repair_suggestion": "Try a fresh explanation or application from Chapter 1 without hints."
    }]
  }
}
```

`readiness` and `repair` are read-only: they do not create locks, change revisions, or append questions. Valid ready/not-ready reports exit 0 and print JSON. Invalid state, a cycle, or an unknown chapter exits nonzero with a readable stderr error.

## Repair drafts

`repair --chapter ch2` lists `needs-practice` outcomes in that chapter and its transitive prerequisites. Other readiness gaps remain in `readiness` but are not reported as demonstrated mistakes. Add `--generate` to include one generic explanation/example question per gap. The helper uses the outcome description; it does not invent subject-specific answers or evaluate them. The teaching agent must check the prompt, select one manageable gap, and prepare criteria before showing it.

Generated question IDs avoid existing question IDs. They are drafts and reserve nothing until explicitly saved. Re-running without a save may return the same IDs. Each generated question uses the outcome's **owning chapter**, preserving the existing question/outcome validation rule:

```json
{
  "id": "repair-oc1",
  "chapter_id": "ch1",
  "outcome_ids": ["oc1"],
  "type": "explanation",
  "prompt": "For this learning goal: 'Identify numerator and denominator', explain the key idea in your own words and give one brief example.",
  "kind": "repair",
  "requires_agent_review": true
}
```

Accept or adapt the draft, append the question, collect an answer, and append an attempt with `kind: repair` and actual assistance. Link the new evidence to the original outcome after evaluation. Repair is a practice purpose, not an assistance level or automatic status change; preserve previous attempts and independent evidence. Do not create a separate repair chapter targeting outcomes it does not own.

## Resource extraction schema

The Phase 1 contract documents the existing extractor accurately. It is independent of learner-state schema version 1. Run `python <skill>/scripts/extract_resource.py <file> --source-id s1`; output is UTF-8 JSON on stdout, with errors on stderr and a nonzero exit code.

```json
{
  "schema_version": 1,
  "source_id": "s1",
  "title": "notes.md",
  "location": "/learner/notes.md",
  "status": "extracted-not-reviewed",
  "limitations": ["Markdown heading detection is ATX-only."],
  "warnings": [],
  "records": [
    {
      "locator": {"line_start": 1, "line_end": 2, "heading": "Fractions"},
      "text": "# Fractions\nA fraction represents a quantity.",
      "warnings": []
    }
  ]
}
```

### Field availability

| Field | Type | Availability |
| --- | --- | --- |
| `schema_version`, `source_id` | integer, string | All successful extractions; version 1 and caller-supplied source ID. |
| `title`, `location`, `status` | strings | All formats; filename, resolved local path, and `extracted-not-reviewed`. |
| `limitations`, `warnings`, `records` | arrays | All formats; warnings do not certify content correctness. |
| `records[].text`, `.warnings`, `.locator` | string, array, object | Every legacy record. |
| `locator.line_start`, `.line_end`, `.heading` | integers, nullable string | Text/Markdown; original 1-based line ranges. |
| `locator.file_page`, `.page_label` | integer, string | PDF; 1-based file page and PDF metadata label, which may differ from a printed label visible on the page. |
| `locator.body_block`, `.kind`, `.heading` | integer, string, nullable string | DOCX; main-body element position, paragraph/table kind, and current heading. DOCX has no reliable source line numbers. |
| `records[].rows` | array of string arrays | DOCX tables; merged cells and nested tables need inspection. |

Legacy `records` group Markdown by heading and PDF by page; they are not guaranteed semantic paragraphs. A low-text PDF warning flags a page for visual/OCR inspection, not a detected image or its meaning. Unsupported formats fail explicitly rather than returning imaginary extracted content.

### Link questions to inspected content

Store the full extraction output separately in the learner workspace. In the Phase 1 format, cite source ID plus exact locator, such as `s1, lines 1–2, heading Fractions` or `s2, file page 7`. Questions may include optional source-location metadata; the state validator does not verify its contents. Read that actual extract before generating the question or showing it in feedback.

When finer block IDs are available, record the extraction identity as well as the block ID; re-extracting an edited document can change positional IDs. Do not pretend an ID fetches live source content automatically. Load the stored JSON, select the record/block, and compare it with the source as needed.

### Phase 4 additions: extraction format 1.1

The updated extractor preserves `schema_version: 1` and `records`, and adds the fields below. Check `metadata.format_version` for `"1.1"`; its absence identifies an older output. This is an additive extraction contract, not a state schema migration.

```json
{
  "source_type": "markdown",
  "extracted_blocks": [
    {
      "block_id": "b1",
      "type": "heading",
      "content": "Fractions",
      "heading_level": 1,
      "heading_path": ["Fractions"],
      "line_range": [1, 1],
      "extraction_status": "success"
    },
    {
      "block_id": "b2",
      "type": "paragraph",
      "content": "A fraction represents a quantity.",
      "heading_path": ["Fractions"],
      "line_range": [2, 2],
      "extraction_status": "success"
    }
  ],
  "metadata": {
    "format_version": "1.1",
    "total_blocks": 2,
    "extraction_date": "2026-09-06",
    "python_version": "3.14.7",
    "source_sha256": "<actual SHA-256 of the extracted file>"
  }
}
```

This example shows only the added fields; each real output also contains the Phase 1 envelope and `records`. Date and Python version reflect the actual extraction environment.

| Added field | Availability and meaning |
| --- | --- |
| `source_type` | All outputs: `text`, `markdown`, `pdf`, or `docx`. |
| `extracted_blocks[].block_id` | All blocks; `b1`, `b2`, etc., unique within this extraction. Stable for unchanged input and extractor version, not stable across document edits. |
| `.type`, `.content`, `.extraction_status` | All blocks. Types: paragraph, heading, code_block, table, or page. Status: success or low_confidence; this describes extraction flags, not semantic correctness. |
| `.heading_path` | Markdown/DOCX hierarchy; `[]` before any heading. Plain text also uses `[]`. Skipped levels do not create invented ancestors. |
| `.heading_level` | Markdown/DOCX heading blocks only. Markdown uses ATX headings; DOCX resolves style names, outline levels, and inherited styles from OOXML. |
| `.line_range` | Text/Markdown only; original 1-based inclusive lines. Code content includes its fences. |
| `.body_block`, `.style_name` | DOCX body location; style name for paragraph/heading blocks. No invented DOCX line numbers or rendered page numbers. |
| `.file_page`, `.printed_page` | PDF page blocks only. `printed_page` holds the PDF metadata label; verify against the visible printed label if needed. PDF pages are not mislabeled as paragraphs. |
| `.table_structure` | DOCX table blocks: basic cell rows, matching legacy `rows`. Advanced merged-cell layout is not reconstructed. |
| `.code_language` | Fenced Markdown code: first info-string token or empty string. This is a source label, not verified language detection. |
| `.warnings` | Blocks with limitations, including low-text PDF pages, unclosed code fences, or DOCX table caveats. |
| `metadata` | Format version, actual block count, UTC extraction date, runtime Python version, and source SHA-256. |

For a question citing b2, store source ID, `metadata.source_sha256`, `metadata.format_version`, block ID, and its locator. These optional question fields remain agent-checked metadata. Reload that exact saved extraction and inspect b2 before presenting it as evidence. If the source hash changed, remap citations instead of silently reusing the positional ID.

### Still planned, not implemented

OCR `extraction_confidence`, image understanding/`image_notice` descriptions, and advanced table layout remain outside the helper. Do not fabricate them. Missing dependencies or unsupported formats return an error rather than invented blocks. DOCX hierarchy extraction uses the standard library to read the same stored style-name/outline information; it does not require a new `python-docx` dependency.
