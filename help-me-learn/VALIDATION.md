# Validation

Validation date: 2026-09-06. Local environment: Windows, Python 3.14.7. Optional validation dependencies: pypdf 6.17.0 and PyYAML 6.0.3, installed in the parent workspace's `.validation-deps`, outside the distributable skill folder.

## Automated checks

Result: all 16 tests passed with PDF support enabled; the skill-creator validator passed in UTF-8 mode, and all relative Markdown links resolved.

The unittest suite covers UTF-8 state and CLI output, valid updates and revisions, stale updates, duplicate JSON keys, invalid evidence links, assisted-versus-independent evidence, preserved attempt/question history, pending hints across resume, exclusive locks, and simulated replacement failure preserving the previous file.

Extraction fixtures cover text, Markdown headings and fenced code, DOCX paragraph/table ordering, PDF text and file page boundaries, PDF page labels, low-text warnings, absent optional PDF support, missing/unsupported files, malformed DOCX, and CLI error handling. The PDF fixture contains one text page and one blank page; this does not validate OCR or arbitrary real-world PDF layout.

Run the checks from the package's parent directory:

```powershell
$env:PYTHONPATH = 'D:\help-me-learn\.validation-deps'
python -m unittest discover -s help-me-learn/tests -v
python -X utf8 C:/Users/HP/.codex/skills/.system/skill-creator/scripts/quick_validate.py help-me-learn
```

These are local developer paths, not required installation paths. The `-X utf8` option avoids the external validator's reliance on Windows' default text encoding. The skill helpers read/write UTF-8 explicitly.

## Instructional walkthroughs

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

### Optional MCP update

Added Excalidraw and Obsidian reference workflows, an Obsidian course-home template, and practical usage prompts. Excalidraw tool discovery and its read-only `read_me` call succeeded in this session. Diagram creation, exports, and Obsidian writes were not live-tested; no Obsidian MCP tools were exposed. This update configures skill behavior, not host connections.

The skill validator passed after this update. All relative Markdown links and heading anchors resolved, and the new template's YAML parsed successfully. The earlier 16-test result applies to the unchanged Python helpers; that suite was not repeated for this documentation/template update.

Author review covered four integration cases: missing tools continue in text; an Excalidraw checkpoint without export is not reported as a vault file; an Obsidian timeout triggers read-back before another write; and a stale note summary is reconciled against the authoritative state revision. These are instructional checks, not live server tests. No Python helpers changed in this update.

Automatic skill discovery and end-to-end behavior in Codex CLI, OpenCode, and Claude Code have not been tested. No clinical effectiveness claim is made. General visualizer guidance is included, but no reusable HTML visualizer or OCR engine is bundled. Host browsing and image inspection require host capabilities. User-source documents remain unchanged.
