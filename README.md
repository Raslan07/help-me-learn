# Help Me Learn

**An adaptive learning skill for people with ADHD or difficulty sustaining attention.**

Bring a topic, PDF, article, or documentation page. Help Me Learn guides your AI agent to break it into chapters, teach one small unit at a time, check your understanding, and explain how to improve your answers.

Designed for agents such as **Codex CLI, Claude Code, and OpenCode**, with optional **Excalidraw** diagrams and **Obsidian** study notes. The core workflow uses Markdown instructions and can run as a text conversation.

[Get started](#get-started) · [How it works](#how-it-works) · [Integrations](#optional-integrations) · [Usage guide](help-me-learn/USAGE.md)

## Get started

With Node.js and `npx` available, install the skill using the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add https://github.com/Raslan07/help-me-learn/tree/main/help-me-learn --skill help-me-learn
```

Follow the prompts to choose your agent. Add `-g` to make it available across projects. The URL points directly to the skill folder inside this repository.

Then ask your agent:

```text
Use the help-me-learn skill.

I want to learn Python functions.
My goal is to write a function with parameters and a return value.
I'm a beginner and have about 15 minutes today.

Teach one small unit at a time and ask questions individually.
Let me attempt the answers before showing solutions.
```

You can provide your own file or URL, choose a different topic, and specify your preferred language. For example: “Explain in Arabic, keeping the technical terms in English.”

For local use without the installer, ask an agent with file access to read [`help-me-learn/SKILL.md`](help-me-learn/SKILL.md). Keep its `references/`, `assets/`, and `scripts/` folders together.

## How it works

```text
Topic or resources → Chapters → Small lessons → Questions
                                                  ↓
Next lesson or saved pause ← Fresh practice ← Answer review
```

1. **Build a roadmap.** Organize the topic around your goal and prerequisites, expanding only the current chapter.
2. **Learn in small units.** Work through one idea, a concrete example, and a short practice task.
3. **Check understanding.** Answer a chapter question set, normally one question at a time. Hints and full solutions are available when you request them.
4. **Review your reasoning.** See what you got right, the specific gap, a worked solution, and why your approach did or did not work. Try a fresh example when needed.
5. **Resume with context.** Save your position, prior hints, remaining gaps, and one next action when file access is available. Otherwise, receive a copyable resume note.

The skill distinguishes guided success from independent understanding. Reading a chapter does not automatically mark it as learned, and skipping a question does not count as an incorrect answer.

## Built around the learner

- **A small starting step:** begin without a long profile questionnaire or elaborate setup.
- **Adjustable pacing:** change the depth, examples, question format, and session length as needed.
- **Useful visuals:** use diagrams and charts to explain relationships, with text equivalents.
- **Specific feedback:** evaluate ideas and reasoning, accepting correct alternative methods.
- **Easy recovery:** return after a distraction or break without automatically restarting the whole course.

These are adaptable design choices, not a claim that everyone with ADHD learns the same way. Help Me Learn provides educational support; it does not diagnose or treat ADHD. See [evidence and adaptation](help-me-learn/references/evidence-and-adaptation.md).

## Resources you can bring

| Resource | How it is handled |
| --- | --- |
| Topic only | Start with general explanations or verified sources when browsing is available. |
| Text and Markdown | Read directly or use the bundled extractor with line and heading locators. |
| PDFs | Use host tools or optional PDF extraction with file page numbers and page labels. Scans may require separate OCR or image inspection. |
| Word documents | Extract main-body paragraphs and tables from `.docx` files. |
| Articles and documentation | Read through the host's browsing tools or use a supplied extract. |
| Diagrams, charts, and visualizations | Inspect through available host capabilities; use a description or text alternative when inspection is unavailable. |

The skill instructs the agent to identify inaccessible content and extraction limits rather than invent missing material. See [resource handling](help-me-learn/references/resources-and-visuals.md).

## Optional integrations

| Integration | Learning use |
| --- | --- |
| **Excalidraw MCP** | Draw and revise concept maps, sequences, and visual explanations using connected tools. |
| **Obsidian MCP** | Save chapter notes, answer reviews, and a course home page with your next action. |

Example request:

```text
Use Excalidraw when a diagram helps explain the current idea.
Save my notes in the Obsidian vault I select, under Learning/Python Functions.
Check which tools are connected. If either integration is unavailable,
continue in text and tell me what has not been saved.
```

> [!NOTE]
> Installing the skill does not install or connect MCP servers. Configure them in your agent separately. A diagram displayed in chat is not automatically saved in Obsidian.

See the [Excalidraw workflow](help-me-learn/references/excalidraw.md) and [Obsidian workflow](help-me-learn/references/obsidian.md) for supported operations, destination handling, and fallbacks.

## Make a session useful

Start with **one concrete outcome and one primary resource**. Attempt the questions in your own words, then use feedback to repair a specific gap. When a diagram appears, explain its relationships instead of only looking at it.

Useful requests:

| When you need… | Say… |
| --- | --- |
| Less information | “Only show the next small step.” |
| A different explanation | “Use another example and check what prerequisite I'm missing.” |
| Help without the answer | “Give me one hint.” |
| A stopping point | “Pause and save my position and next action.” |
| To return later | “Resume from my saved course record and give me one recall question.” |

For a new agent session, provide the saved course location. Persistent memory depends on accessible saved records. More examples are in the [usage guide](help-me-learn/USAGE.md).

## Package contents

```text
help-me-learn/
├── SKILL.md          # Core teaching instructions
├── USAGE.md          # Practical prompts and usage guidance
├── VALIDATION.md     # Checks performed and known limits
├── references/       # Assessment, source handling, state, and MCP workflows
├── assets/           # Chapter, review, resume, and Obsidian templates
├── scripts/          # Resource extraction and session-state helpers
└── tests/            # Helper regression tests
```

The Python helpers are optional. `session_state.py` uses the standard library to validate and save progress. `extract_resource.py` supports text, Markdown, and DOCX with the standard library; PDF extraction needs `pypdf` in the Python environment running the script:

```bash
python -m pip install pypdf
```

Keep learner answers and progress in a separate workspace or selected vault. See [state schema and commands](help-me-learn/references/state-schema.md) before using the helpers directly.

## Validation and compatibility

The local helper suite passed **16 tests** on Windows with Python 3.14.7, including PDF extraction, Unicode output, state validation, and failed-write recovery. The skill structure, reference links, and template YAML were also checked.

Run the helper tests from the repository root:

```bash
python -m unittest discover -s help-me-learn/tests -v
```

PDF integration tests skip if `pypdf` is absent. End-to-end installation and teaching behavior across all three CLIs have not been tested. MCP exports, vault writes, OCR, and rendering depend on the connected tools. Full details: [validation report](help-me-learn/VALIDATION.md).
