# Validation

Validation date: 2026-09-06. Local environment: Windows, Python 3.14.7. Optional validation dependencies: pypdf 6.17.0 and PyYAML 6.0.3, installed in the parent workspace's `.validation-deps`, outside the distributable skill folder.

## Automated checks

Original baseline: 16 tests passed with PDF support enabled. The enhancement suite now contains 36 tests, including that baseline; results and scope are recorded below.

The unittest suite covers UTF-8 state and CLI output, valid updates and revisions, stale updates, duplicate JSON keys, invalid evidence links, assisted-versus-independent evidence, preserved attempt/question history, pending hints across resume, exclusive locks, and simulated replacement failure preserving the previous file.

Extraction fixtures cover text, Markdown headings and fenced code, DOCX paragraph/table ordering, PDF text and file page boundaries, PDF page labels, low-text warnings, absent optional PDF support, missing/unsupported files, malformed DOCX, and CLI error handling. The PDF fixture contains one text page and one blank page; this does not validate OCR or arbitrary real-world PDF layout.

Run the checks from the package's parent directory:

```powershell
$env:PYTHONPATH = 'D:\help-me-learn\.validation-deps'
python -m unittest discover -s help-me-learn/tests -v
python -X utf8 C:/Users/HP/.codex/skills/.system/skill-creator/scripts/quick_validate.py help-me-learn
```

These are local developer paths, not required installation paths. The `-X utf8` option avoids the external validator's reliance on Windows' default text encoding. The skill helpers read/write UTF-8 explicitly.

## Enhancement implementation

Implemented all four phases in `help-me-learn-improvements-prompt.md`, including the optional heading extraction and repair helpers. No README styling or UI behavior changed.

| Scope | Verification |
| --- | --- |
| Assessment generation | Separate generation reference covers E/A/T/W patterns, coverage limits, acceptance criteria, anti-priming, and domain examples. Linked from the skill and grading reference. |
| Canonical progress | JSON and notes-only decision paths, mode metadata, legacy metadata mapping, partial-save states, expected summary drift, and substantive conflicts documented. Course-home template aligned. |
| Readiness | Tests cover all evidence statuses, omitted/empty dependencies, shared and transitive prerequisites, invalid references, self/long cycles, unknown chapters, and a 1,101-outcome graph without recursion failure. |
| Repair | Tests verify chapter/owner alignment, collision-free draft IDs, valid repair attempts, no-gap behavior, and read-only CLI output preserving original files. |
| Extraction | Tests cover nested/skipped/sibling headings, fenced code, multiline paragraphs, style-name inheritance, DOCX tables, hashes, block IDs, and preserved legacy records. PDF page blocks retain labels and low-text warnings. |
| MCP resilience | Author-reviewed deadline examples and failure scenarios. No live timeout, cancellation, retry, note-write, or diagram-export experiment was performed. Host controls are required to enforce 5s/2s deadlines. |

### Reconciliations with the supplied examples

- The Phase 1 extraction example is now the actual legacy `records` contract; Phase 4 adds `extracted_blocks` and metadata under format 1.1 without removing it. PDF blocks are pages; DOCX gets body locators, not invented lines. OCR confidence and image descriptions remain unimplemented.
- A numerator can be zero. Question-generation examples correct that misconception and do not infer outcome coverage from question count.
- `demonstrated-with-help` is a readiness gap; this report does not prevent the learner from proceeding. Repair questions target the original outcome's chapter, preserving existing state validation.
- DOCX hierarchy reads stored style names, inheritance, and outline levels directly with the standard library, avoiding an extra `python-docx` dependency.
- Drawing retries are bounded and require a safe existence/idempotency check. The prompt's more specific Obsidian rule takes precedence over its general retry example: no automatic note-write retries. Unknown completion stays unknown.
- A stale derived note is normal in JSON mode. Substantive disagreement is resolved with the learner before changing authority; existing notes are not archived simply because both files exist.

### Result

All 36 tests passed with PDF support enabled. Skill/frontmatter, template YAML, relative links, and documentation examples are checked separately from behavioral tests. MCP deadlines and persistence policy are instructions rather than an implemented transport wrapper. Existing version 1 state files without prerequisites remain valid; the added `repair` attempt kind requires the updated helper.

## Original instructional walkthroughs

The following are author-reviewed example interactions, not independent model evaluations or live tests in three CLI products.

### Topic only, five minutes

Learner: “Teach me fractions. I have five minutes.”

Suitable first turn: “We'll start with what a fraction means. The roadmap is meaning, comparison, then addition; today we'll do the first small part. In 3/4, the whole is divided into four equal pieces and we take three. If a pizza has eight equal slices and you take three, what fraction did you take?”

Review: Gives a labeled small scope, compact roadmap, example, and one action without a profile questionnaire. It does not teach all chapters in one turn.

### Mixed answers and an alternative solution

Chapter set: identify the denominator's role, add 1/2 + 1/3, and compare 3/4 with 2/3. Learner answers: “number of equal pieces,” “2/5 by adding tops and bottoms,” and “3/4 because .75 is greater than .666 repeating.”

Suitable review: Credit the first answer. Explain why the second needs common-sized pieces: 3/6 + 2/6 = 5/6, then give a fresh retry. Credit the decimal comparison as a valid alternative, without requiring the answer key's cross-multiplication method. Mark addition needs-practice while keeping separate evidence for the other outcomes.

Review: Feedback targets an actual error and does not penalize a correct alternative method or generalize one gap to the whole topic.

### Scanned resource or inaccessible URL

Suitable response: “I couldn't read the figure on file page 2. Please provide its labels or a readable copy of that page. We can continue with the readable definition on page 1.” For an inaccessible URL with no other source, identify the access failure and offer general introductory teaching clearly labeled as such.

Review: No invented figure description or claim of complete source coverage. Low extracted text remains a flag for inspection, not proof that a page is blank.

### Resume after a break

Saved position: chapter c1, unit u1, question q1, paused, hint already given. Suitable response: “You paused on adding fractions. The hint was to use equal-sized pieces. What common denominator could you use for 1/2 and 1/3?”

Review: Resumes the pending question with assistance visible, offers a small retrieval step, and does not erase prior history or claim this is an unassisted attempt. The state round-trip for this case is also tested automatically.

### Text-only host

Learner asks for an interactive comparison of fractions, but no browser, scripts, or file writes are available. Suitable fallback: explain equivalent fractions with a small text table and ask the learner to predict one comparison. End a pause with a copyable resume note that includes position, question, assistance, and next action.

Review: The same learning relationship remains available without a visual renderer. No false claim of saved files, persistent memory, or automatic reminders.

## Limits

### Earlier optional MCP update

Added Excalidraw and Obsidian reference workflows, an Obsidian course-home template, and practical usage prompts. Excalidraw tool discovery and its read-only `read_me` call succeeded in this session. Diagram creation, exports, and Obsidian writes were not live-tested; no Obsidian MCP tools were exposed. This update configures skill behavior, not host connections.

The skill validator passed after this update. All relative Markdown links and heading anchors resolved, and the new template's YAML parsed successfully. The earlier 16-test result applies to the unchanged Python helpers; that suite was not repeated for this documentation/template update.

Author review covered four integration cases: missing tools continue in text; an Excalidraw checkpoint without export is not reported as a vault file; an Obsidian timeout triggers read-back before another write; and a stale note summary is reconciled against the authoritative state revision. These are instructional checks, not live server tests. No Python helpers changed in this update.

Automatic skill discovery and end-to-end behavior in Codex CLI, OpenCode, and Claude Code have not been tested. No clinical effectiveness claim is made. General visualizer guidance is included, but no reusable HTML visualizer or OCR engine is bundled. Host browsing and image inspection require host capabilities. User-source documents remain unchanged.
