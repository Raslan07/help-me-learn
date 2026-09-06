# Use help-me-learn

Keep this entire folder together. In an agent that can read local Markdown, use a request such as:

```text
Read D:/help-me-learn/help-me-learn/SKILL.md and follow it for this learning session.
I want to learn fractions. I have 10 minutes and want to add unlike fractions.
Save my progress in D:/help-me-learn/my-learning/fractions when file access is available.
```

Replace the topic and paths with your own. You can also provide PDFs, articles, documentation, documents, diagrams, or charts. With no file reader, paste the skill instructions and supply any referenced guidance needed for the task. The agent can teach in plain text without running helpers.

The shared skill uses only Markdown, relative resource links, and basic name/description frontmatter. Codex CLI, OpenCode, and Claude Code installation/discovery behavior has not been tested here. This package makes no claim of automatic discovery or identical capabilities across those hosts. Explicit local-file loading requires a host with that capability.

## Optional helpers

For optional MCP workflows and a ready-to-copy starting prompt, see [Using the integrations and studying effectively](#using-the-integrations-and-studying-effectively).

- `scripts/session_state.py`: save/validate progress, check declared prerequisites with `readiness`, and suggest generic gap questions with `repair --generate`. The last two commands are read-only. Python standard library only; see [commands and schema](references/state-schema.md).
- `scripts/extract_resource.py`: local UTF-8 text/Markdown and DOCX extraction with the standard library. PDF extraction requires optional `pypdf`. See [source handling](references/resources-and-visuals.md).

Example diagnostic commands (replace the paths and chapter ID with your course's values):

```text
python <skill>/scripts/session_state.py readiness <learner>/state.json --chapter ch2
python <skill>/scripts/session_state.py repair <learner>/state.json --chapter ch2 --generate
```

Readiness reports gaps including prerequisites demonstrated only with help. The learner can still continue. Repair output contains generic drafts for agent review; it does not save questions or grade answers. Extraction now includes a finer block view with heading paths while preserving existing `records` consumers.

If PDF extraction is needed and installation is permitted, install `pypdf` in the Python environment used to run the helper. Browsing, OCR, chart inspection, and HTML rendering depend on the host. The skill gives fallbacks rather than requiring them.

Reusable output templates live in `assets/`; agent guidance lives in `references/`. A generic visualizer, flashcard exporter, and review scheduler are intentionally deferred until an actual lesson needs them. The agent can create a focused visualizer from the documented guidance without a universal template.

## Development checks

From this package's parent directory:

```text
python -m unittest discover -s help-me-learn/tests -v
```

PDF integration tests skip if `pypdf` is absent. [Validation notes](VALIDATION.md) distinguish automated checks from instructional walkthroughs and untested host integrations.

## Using the integrations and studying effectively

The skill now includes [Excalidraw guidance](references/excalidraw.md), [Obsidian guidance](references/obsidian.md), and an [Obsidian course-home template](assets/obsidian-course.md). MCP servers must be connected in the agent you are using. This package update does not configure those connections.

Before the first persistent save, select [one authoritative progress record](references/obsidian.md#canonical-source-choose-one): JSON state with derived notes, or a notes-only `Start.md`. Use the same choice on resume. The [resilience guide](references/integration-resilience.md) defines bounded requests where the host supports timeouts, safe drawing retries, and no automatic Obsidian write retries.

First, ask the agent to check the tools actually available. Excalidraw's [official MCP App](https://github.com/excalidraw/excalidraw-mcp) supports interactive diagrams in compatible hosts. Obsidian's [Local REST API with MCP](https://github.com/coddingtonbear/obsidian-local-rest-api) is a community option for vault access. Use each server's current instructions and your host's configuration format; do not copy another CLI's configuration blindly.

### Start with a concrete outcome

Copy this and replace the bracketed values. The vault folder is relative to your selected vault, not an absolute filesystem path:

```text
Read D:/help-me-learn/help-me-learn/SKILL.md and use it for this session.

Topic: [Python functions]
Goal: [Write and explain a function with parameters and a return value]
Starting level: [Beginner]
Time today: [15 minutes, adjustable]
Language: [English / Arabic / Arabic with English technical terms]
Resources: [One file path or URL, or use general introductory teaching]

Use connected Excalidraw MCP tools when a diagram makes the idea clearer.
Use connected Obsidian MCP tools to create and update this course's notes:
Vault: [my selected vault]
Course folder: Learning/Python Functions
Preserve unrelated notes. Check which integrations are available first.
If either is unavailable, continue in text and clearly identify unsaved work.

Teach one small unit at a time. Ask chapter questions one at a time.
Let me attempt them before showing solutions. Record hints as assistance.
At pause, save my exact position and one next action when possible.
```

If you have no vault selected yet, omit the Obsidian lines and begin in chat. Supply the destination when you want to save.

### A practical session routine

1. Choose one outcome and one primary source to begin. Add another resource when a specific gap needs it.
2. Work through one small unit. Explain or apply the idea yourself before asking for more material.
3. Use the diagram actively: predict an arrow's meaning, redraw the relationship, or explain what changes. Ask for simpler text if the picture distracts you.
4. Attempt the chapter questions in your own words. Ask for a hint when stuck; after feedback, try a fresh example.
5. Say “Pause and save my next action.” On return, request the saved course record and one retrieval check.

These are starting defaults, not a prescribed ADHD routine. Adjust the pace, language, difficulty, and amount of visual detail from actual experience. Save useful explanations and mistakes; avoid producing a large note collection before doing any practice.

### Useful requests during study

| Situation | Say |
| --- | --- |
| Too much information | “Only show the next small step.” |
| Explanation unclear | “Use a different example and check the prerequisite I may be missing.” |
| Want a diagram | “Draw this relationship in Excalidraw, then ask me to explain it.” |
| Ready for assessment | “Quiz me on this chapter without showing answers yet.” |
| Returning later | “Resume Learning/Python Functions/Start.md in my selected vault. Check the authoritative progress record and give me one recall question.” |

For a new agent or CLI, provide the skill path and the same saved course location. An old conversation or Excalidraw checkpoint alone is not portable memory. Use one agent at a time for the same course's progress to reduce conflicting updates.
