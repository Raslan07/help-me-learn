# State and helper commands

Use the agent's normal file tools if Python is absent. Follow the same schema and preserve prior attempts. With no writable workspace, use the [resume template](../assets/resume.md) in the conversation. State may contain learner answers: keep it local and out of the distributed skill.

## Commands

Replace `<skill>` and `<learner>` with actual paths; quote paths containing spaces. The destination parent directory must already exist. Python 3.10+ is the intended runtime; tests were run on the version recorded in the validation report.

```text
python "<skill>/scripts/session_state.py" init "<learner>/state.json" --topic "Fractions" --goal "Add unlike fractions"
python "<skill>/scripts/session_state.py" show "<learner>/state.json"
python "<skill>/scripts/session_state.py" validate "<learner>/state.json"
python "<skill>/scripts/session_state.py" update "<learner>/state.json" --from "<learner>/candidate.json"
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

Outcome records require `id`, `description`, `status`, and `evidence_attempt_ids`. IDs must be globally unique for outcomes and unique within other record collections; unit IDs need only be unique within a chapter. Question outcomes must belong to their chapter. Evidence must reference an attempt that actually targets that outcome.

Outcome statuses: `unassessed`, `needs-practice`, `demonstrated-with-help`, `demonstrated-independently`. All assessed statuses need evidence; independent status requires at least one unassisted attempt. The helper checks structure and links, not answer correctness. The agent must judge whether evidence supports the label.

Assistance: `none`, `hint`, `solution`. Attempt kinds: `practice`, `chapter-check`, `retry`, `delayed-retrieval`. Delayed retrieval also requires `date` as an ISO date, for example `2026-09-06`. Other attempts may include a date too. Store hints and criteria as optional additional fields when needed. Additional JSON fields are preserved but not validated beyond core schema requirements.

Save a submitted answer immediately with empty feedback if review is pending. Because attempts are immutable through the helper, append a reviewed record with a new ID, the same answer and assistance, and optional `supersedes_attempt_id` referencing the pending record. Point outcome evidence to the reviewed record. Use the same approach to correct mistaken feedback; preserve the history and do not count superseded records as separate successes.

While awaiting an answer, keep assistance already given in `position.assistance` and the hint texts in `position.hints`. Copy that assistance into the submitted attempt, then reset these position fields when moving to a new question. This prevents a pause from turning a hinted answer into apparently independent evidence.

Questions with attempts cannot be changed through updates. If the key or prompt was flawed, create a corrected question with a new ID and record the correction. Make fresh retry questions distinct from the original.

`position.phase: complete` means the planned journey ended, not that all outcomes were mastered. Leave skipped outcomes unassessed. Save a new topic in a new state file.
