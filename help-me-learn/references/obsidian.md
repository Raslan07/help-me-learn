# Optional Obsidian MCP integration

Use Obsidian as the learner's organized study record when requested. Read and write through the actual connected server's documented tools. The [Local REST API with MCP community plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) is one option supporting note access, search, and targeted updates. This is a community integration, not a required or bundled dependency. Documentation checked 2026-09-06.

## Establish the destination

Use the learner's specified vault and course folder. If more than one vault is possible or no destination is known, ask for the destination before dependent writes and continue teaching in chat. Do not ask again after the learner has authorized that destination. Confirm access with a bounded list or read, rather than searching the entire vault unnecessarily.

Discover supported read, create, patch, search, attachment, and UI operations. Do not assume a Markdown-only server accepts JSON or binary files. Keep API keys in the host's connection settings, never in notes, prompts, or skill assets. No MCP setup or Obsidian plugin installation is implied by loading this skill.

## Minimal course structure

Adapt to an existing organization. For a new course, this is a suggested layout, not a required upfront scaffold:

```text
Learning/<course>/
  Start.md
  Chapters/01 - <chapter>.md
  Reviews/01 - <chapter> - <review-id>.md
  Diagrams/<actual-exported-file>
```

Create only files needed now. `Start.md` holds the goal, compact roadmap, current position, next action, and links to existing chapters/reviews. A chapter holds outcomes, source locators, examples, and the learner's notes. Reviews hold submitted answers, specific feedback, assistance, and fresh retries. Keep unrevealed answer keys out of learner-facing notes; folded callouts are not hidden storage.

Use [the course-home template](../assets/obsidian-course.md) for `Start.md`, [chapter](../assets/chapter.md) for lessons, and [answer review](../assets/answer-review.md) for feedback. Fill fields and remove unused sections before saving. Preserve existing user properties, tags, and headings.

The course-home template starts in notes-only mode. For an existing or selected JSON course, replace its `canonical_source`, `note_revision`, and `last_updated` fields with the mode A metadata below before saving. The template must not override an established course mode.

Use vault-relative wikilinks to verified targets, preferably including the course path to avoid duplicate-name ambiguity. For example, `[[Learning/Fractions/Chapters/01 - Equal pieces|Equal pieces]]`. Embed an existing image with `![[Learning/Fractions/Diagrams/equal-pieces.png]]`; also include a text explanation. Use standard Markdown links for external sources. Do not create a link to a planned file and report it as saved.

## Safe, repeatable updates

Read the target note immediately before updating. Prefer supported heading/block patches, preserving unrelated content. If only full replacement exists, merge into freshly read content and use version checks where available. If concurrent edits cannot be checked, create a separate update note rather than risk replacing the learner's work.

Use stable course/chapter IDs and review IDs to find existing output before creating another copy. After a timeout, read/search that target before retrying. Read back the result to verify the intended section, source links, and next action. Inspect Obsidian reading view when available; otherwise report that content was checked but rendering was not.

## Canonical source: Choose one

Choose the authoritative progress record before the first persistent save. Use the learner's stated preference; otherwise choose A when an authorized JSON location is available, B when only note storage is available. With neither, provide a copyable resume note and do not claim persistence. Storage selection must not delay the first lesson.

### Mode A: JSON state is authoritative

Choose this for validated, versioned progress with file access. Save `state.json` in the authorized workspace or vault. `Start.md` and progress summaries are derived views; learner annotations and source notes remain their own content.

Save state with [the helper](state-schema.md), then save the primary review note and update the course summary. On resume, read JSON first and refresh stale derived sections. A failed note update does not undo a confirmed state save. A failed state write leaves the prior revision intact when using the helper; keep the new work in a copyable draft. Do not describe a note failure as harmless if that note contains learner content not stored elsewhere.

Example `Start.md` metadata (relative paths resolve from this note's folder):

```yaml
---
canonical_source: json
state_location: "state.json"
state_revision: 5
last_synced: "2026-09-06"
---
```

`state_revision` is the JSON revision actually reflected in this note. Update `last_synced` only after the note is confirmed saved. An absolute state location is acceptable when the JSON is outside the vault; do not confuse it with a vault-relative note path.

### Mode B: Start.md is authoritative

Choose this for note-only access or a learner who prefers manual note management. Do not maintain an independently evolving JSON state file for the same course. `Start.md` holds the complete resume record; linked review notes hold answer evidence.

Maintain current chapter/unit/question, prior hint text, demonstrated outcomes with dates, open gaps, and one next action. Increment the note revision when progress changes. Read before writing and preserve manual edits. This mode does not provide the state helper's validation, atomic replacement, or rollback guarantees. If saving fails, the new progress is unconfirmed; retain a draft rather than assuming all previous progress was lost.

```yaml
---
canonical_source: notes
note_revision: 3
last_updated: "2026-09-06"
---
```

### Existing metadata and switching modes

Existing `progress_mode: structured-state` maps to `canonical_source: json`; `notes-only` maps to `notes`. Interpret `progress_record` and `progress_revision` accordingly. Preserve the current choice on resume. When updating metadata, migrate consistently; if legacy and new fields disagree, resolve the conflict first.

Do not switch silently mid-course. If a switch is necessary, export and verify the current record, preserve an archived copy without overwriting an existing archive, and create a new course record in the new mode linked to the old one. Mark the old record archived only after the new record is verified. Do not rename or move files merely because the alternate mode is unavailable during one session.

### Conflict resolution

An older derived summary with a known JSON revision is expected drift: refresh only its derived sections. Both files existing is normal in mode A and is not by itself a conflict.

If records disagree substantively, the authoritative mode is missing, or the learner edited progress in a derived note, read both records and compare revisions and timestamps. Timestamps help explain history but do not establish correctness. Ask which progress is correct before replacing it; preserve both originals until resolution. Record the chosen authority and reconcile or archive the superseded progress record without deleting unrelated notes or annotations. Do not silently choose whichever file is newest.

## Excalidraw handoff

The Excalidraw MCP server, Obsidian MCP server, and Obsidian's Excalidraw plugin are separate capabilities. Connecting both MCP servers does not automatically synchronize a scene into the vault. Use an actually supported export and attachment write. Editable plugin-specific formats require verified plugin compatibility; otherwise save an available image export and text explanation. If no export exists, link a real returned URL or mark the diagram session-only.

## Failure path

If the vault is unavailable, continue the lesson and produce a copyable note or save to an already authorized local fallback. Clearly label it unsynced and record the intended vault-relative destination. After an ambiguous write, check its result before considering a later learner-requested retry; do not automatically retry writes. Do not mark any note or attachment saved until verified.


## Timeouts and sequential writes

Read [integration resilience](integration-resilience.md) before writes. Use a 5-second write timeout and a 2-second verification read when supported by the host. This documentation cannot override a host's fixed timeout.

In JSON mode save state first, then the primary review note, then secondary links and summaries. If a primary is unconfirmed, stop dependent writes. If a secondary fails, report the saved primary and the failed secondary independently. In notes-only mode, a failed `Start.md` update leaves the resume record stale even when a review saved.

Do not automatically retry Obsidian writes, including after authentication or availability failures. A read-back check may confirm a timed-out write; an unknown result must stay unknown. These steps preserve partial results but do not create atomicity across notes.
