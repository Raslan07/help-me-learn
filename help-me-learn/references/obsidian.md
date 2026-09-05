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

Use vault-relative wikilinks to verified targets, preferably including the course path to avoid duplicate-name ambiguity. For example, `[[Learning/Fractions/Chapters/01 - Equal pieces|Equal pieces]]`. Embed an existing image with `![[Learning/Fractions/Diagrams/equal-pieces.png]]`; also include a text explanation. Use standard Markdown links for external sources. Do not create a link to a planned file and report it as saved.

## Safe, repeatable updates

Read the target note immediately before updating. Prefer supported heading/block patches, preserving unrelated content. If only full replacement exists, merge into freshly read content and use version checks where available. If concurrent edits cannot be checked, create a separate update note rather than risk replacing the learner's work.

Use stable course/chapter IDs and review IDs to find existing output before creating another copy. After a timeout, read/search that target before retrying. Read back the result to verify the intended section, source links, and next action. Inspect Obsidian reading view when available; otherwise report that content was checked but rendering was not.

## One progress record

Select one mode per course and record it in `Start.md`:

- **Structured state:** Keep the existing schema in one authorized `state.json` file, either in the course folder if supported or in a separate local learner workspace. Use [the state helper](state-schema.md) where possible. Put its exact location and last reflected revision in `Start.md`. Markdown notes summarize this state; they do not become a second independent progress database.
- **Notes only:** If JSON/file execution is unavailable, make `Start.md` the authoritative resume record and reviewed notes the evidence history. Record current chapter/unit/question, prior hints, demonstrated outcomes, open gaps, one next action, and a monotonically increasing note revision. This is a human-readable fallback, not state-helper validation or atomic-write protection.

With structured state, save attempts and progress first, then update the notes and their reflected revision. If note saving fails, report that state saved but notes did not. If state saving fails, retain the update in a copyable draft and do not claim the new progress is persisted. On resume, compare revisions and rebuild stale summaries from the authoritative record without overwriting user annotations. Do not silently switch modes or overwrite conflicting records.

## Excalidraw handoff

The Excalidraw MCP server, Obsidian MCP server, and Obsidian's Excalidraw plugin are separate capabilities. Connecting both MCP servers does not automatically synchronize a scene into the vault. Use an actually supported export and attachment write. Editable plugin-specific formats require verified plugin compatibility; otherwise save an available image export and text explanation. If no export exists, link a real returned URL or mark the diagram session-only.

## Failure path

If the vault is unavailable, continue the lesson and produce a copyable note or save to an already authorized local fallback. Clearly label it unsynced and record the intended vault-relative destination. Retry a failed operation only after checking its result; avoid duplicate review notes. Do not mark any note or attachment saved until verified.
