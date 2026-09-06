# Help Me Learn: Enhancement Implementation Prompt

**Status:** Production-ready skill with documented gaps. This prompt covers 6 major improvements in 3 phases.

**Context:** You are enhancing an educational learning skill (`help-me-learn`) built for adaptive, resumable learning with optional Obsidian and Excalidraw integrations. The skill uses a structured JSON state schema, pedagogical patterns, and Python helper scripts.

**Scope:** Code, docs, schema changes, and Python helper extensions. No UI changes. All changes backward-compatible or marked with schema version bump.

---

## Phase 1: Documentation Only (3–4 hours, High ROI)

These are pure docs changes that unblock later phases and clarify design intent.

### 1.1 Create `help-me-learn/references/assessment-generation.md`

**Purpose:** Generative patterns for creating coherent question sets. Currently you have *evaluation* guidance (how to grade) but not *generation* guidance (how to create).

**Content structure:**

```markdown
# Assessment: Generating question sets

## When to use this reference

Use when creating a question set for a new chapter or custom topic. 
This complements assessment.md (grading) with generation patterns.

## Base pattern: 3–5 questions per outcome set

For each outcome in the chapter, you need evidence from multiple angles:

### 1. Explanation check (E-type)
- Learner restates the core idea in own words
- No calculation/code yet, just conceptual clarity
- Example: "What does the numerator tell you?"
- Confirms: Did they grasp the definition?

### 2. Application (A-type)
- Apply the idea to a concrete case, slightly different from taught example
- Same concept, new numbers/scenario
- Example: "Draw 3/5 as a rectangle. Show why you divided it that way."
- Confirms: Can they use the idea, not just repeat it?

### 3. Transfer or misconception (T-type)
- Push an edge case or common wrong answer
- Show when the idea breaks or contradicts intuition
- Example: "Is 5/3 bigger or smaller than 1? How do you know?"
- Confirms: Do they understand *why*, not just the procedure?

### 4. Optional: Worked reverse (W-type)
- Given a solution/answer, explain the steps backward
- Requires justifying each step, not just following a procedure
- Example: "Explain why 1/2 + 1/4 = 3/4. What did someone do first?"
- Confirms: Can they justify reasoning, not memorize?

## Mapping outcomes to questions

| Questions per outcome | Recommended | When |
|----------------------|-------------|------|
| 1 | E-type only | Quick check, 15min session, high confidence prerequisite |
| 2 | E + A | Standard; shows definition + application |
| 2–3 | E + A + T | Deep coverage; catches misconceptions |
| 3+ | E + A + T + W | Mastery-level; retention required |

Do not force all question types for all outcomes. A 5-question set covering 5 outcomes might be:
- Q1: E for outcome 1
- Q2: A for outcome 1
- Q3: E+A combined for outcome 2
- Q4: T for outcome 2 (misconception)
- Q5: E for outcome 3

Total outcomes tested: 3. Total depth per outcome: 1–2 angles.

## Sequencing questions in a set

1. **Easier first:** Explanation before application
2. **Separate concepts:** Don't let Q1 answer prime the correct answer to Q2
3. **Save misconceptions late:** After they've shown competence, challenge the edge case

Example sequence:
1. E: "What is a fraction?" → ✓ Establishes baseline
2. A: "Draw 2/3" → ✓ Shows they can apply
3. T: "Is 3/2 a fraction?" → ✓ Now push the boundary

## Question phrasing: Avoid priming

❌ Bad: "The numerator, which you learned is the TOP number, tells you what?"
→ The prompt hints the answer.

✓ Good: "What does the numerator tell you?"
→ No structure given. Learner must recall.

For open-ended: "Show your work" or "Explain your reasoning" is clearer than "Why?" alone.

## Answer keys and acceptance criteria

For each question, define **before** collecting answers:

1. **Core insight:** What evidence of understanding are you looking for?
   - Example: "Understands that numerator = number of pieces selected"
   
2. **Acceptable variations:**
   - Different wording? (e.g., "top number" vs "numerator")
   - Different representation? (visual vs verbal vs numeric)
   - Partial credit boundaries?

3. **Misconceptions you're watching for:**
   - Confuses numerator ↔ denominator
   - Treats fraction as two separate numbers
   - Thinks 5/3 < 1 always

Document this separately from the question prompt (in your session state or agent notes, not shown to learner).

## Custom topic: Rapid question generation

If a learner brings a topic without prepared questions:

1. Extract the 3–5 taught outcomes from the lesson
2. For each outcome, pick ONE question type (E or A, usually)
3. Generate 3–5 total questions, not 10+
4. Learner attempts them; you evaluate live and adjust feedback depth

This is acceptable because you're assessing, and you can ask follow-ups. 
Reserve fuller question sets for high-stakes or repeated assessments.

## Common patterns by domain

### For procedural skills (math, coding)
- E: "Describe the steps"
- A: "Apply to a new problem"
- T: "What if this constraint changes?"
- W: "Trace through this worked solution"

### For conceptual skills (history, philosophy, design)
- E: "Summarize the main claim"
- A: "Apply to a new historical/design scenario"
- T: "What's a counterargument?"
- W: "Given a conclusion, argue backward"

### For creative/synthesis skills (writing, composition)
- E: "What technique is this?"
- A: "Try it in your own piece"
- T: "When does this technique fail?"
- W: "Analyze this published example"

```

**Acceptance Criteria:**
- [ ] Document is ~600 words, includes patterns + examples
- [ ] Maps outcomes → question types with ratios (1–2 angles per outcome)
- [ ] Includes misconception-watching guidance
- [ ] Provides domain-specific quick reference (math, conceptual, creative)
- [ ] Marked as optional reference in SKILL.md table

---

### 1.2 Update `help-me-learn/references/obsidian.md` — Canonical source model

**Current issue:** "Structured state vs Notes only" is described but the decision tree is vague. Learners don't know when state and notes diverge, what to trust.

**Changes:**

Replace this section:
```markdown
## One progress record

Select one mode per course and record it in `Start.md`:

- **Structured state:** Keep the existing schema in one authorized `state.json` file...
- **Notes only:** If JSON/file execution is unavailable...
```

With this:

```markdown
## Canonical source: Choose one

Before session 1, pick where truth lives. This prevents silent sync drift.

### Mode A: JSON state file is authoritative

**For:** Learners with file storage access who want durable progress records

Location: `state.json` in workspace or vault  
Status: `Start.md` reflects this state; notes are derived views  
Failure mode: If notes fail to save, that's a display glitch; state is safe  
Cost: Notes can drift if manually edited; regenerate on resume  

Workflow:
1. Agent saves state first (atomic, versioned)
2. Agent regenerates derived notes from state
3. If note save fails → report error, but state is persisted
4. On resume: read state.json, rebuild notes if stale

Resume record in `Start.md`:
```yaml
---
canonical_source: json
state_location: "<relative path to state.json>"
state_revision: 5
last_synced: 2026-09-06
---
```

### Mode B: Start.md (notes) is authoritative

**For:** Learners in vault-only workflows; no file system access

Location: `Start.md` in vault  
Status: No JSON state file; this note is your entire resume record  
Failure mode: If `Start.md` save fails, you lose progress (no rollback)  
Benefit: Full manual control; edit notes freely without sync concerns

Fields to maintain in `Start.md`:
- Current chapter / unit / question
- Prior hints given (text, not data structure)
- Demonstrated outcomes with dates
- Open gaps (brief bullet list)
- One next action (one sentence)
- Note revision number (increment manually)

Resume record:
```yaml
---
canonical_source: notes
note_revision: 3
last_updated: 2026-09-06
---
```

### Switching modes mid-course

Do not switch. If you must:
1. Export the current source to a new file
2. Rename the old file `.archived`
3. Start a new course in the new mode
4. Link the old course from the new one

Mixing modes causes irreconcilable sync conflicts.

### Conflict resolution

If `Start.md` and `state.json` disagree (both exist):

1. Read both files, check timestamps
2. Ask learner: "Which is correct — your notes or the saved state?"
3. Use the answer as authoritative; archive the other

Do not silently pick one.
```

**Acceptance Criteria:**
- [ ] Decision tree is explicit (choose A or B upfront)
- [ ] Failure modes are documented per mode
- [ ] Resume record examples show canonical source + metadata
- [ ] Conflict resolution is addressed
- [ ] Marked as REQUIRED reading in SKILL.md intro

---

### 1.3 Update `help-me-learn/references/state-schema.md` — Add resource extraction format

**Current gap:** You describe state schema but extraction JSON format is not specified.

**Addition:** New section after "Schema version 1" table:

```markdown
## Resource extraction schema (Phase 1 implementation)

When using `python scripts/extract_resource.py <file> --source-id s1`, 
the output follows this structure:

```json
{
  "source_id": "s1",
  "source_type": "pdf",
  "extracted_blocks": [
    {
      "block_id": "b1",
      "type": "paragraph",
      "content": "The quick brown fox jumps...",
      "file_page": 3,
      "line_range": [42, 48],
      "extraction_status": "success"
    },
    {
      "block_id": "b2",
      "type": "image_notice",
      "content": "[Image: diagram of a cell, no extractable text]",
      "file_page": 3,
      "extraction_status": "low_confidence"
    }
  ],
  "metadata": {
    "total_blocks": 42,
    "extraction_date": "2026-09-06",
    "python_version": "3.10"
  }
}
```

### Field reference

| Field | Type | Always present | Notes |
|-------|------|----------------|-------|
| `source_id` | string | ✓ | ID you provided (s1, s2, etc) |
| `source_type` | string | ✓ | "pdf", "markdown", "docx" |
| `block_id` | string | ✓ | Unique within source (b1, b2, ...) |
| `type` | string | ✓ | "paragraph", "heading", "table", "image_notice", "code_block" |
| `content` | string | ✓ | Extracted text or description |
| `file_page` | integer | PDF only | Page number (1-indexed) |
| `line_range` | [int, int] | Markdown, DOCX | Start and end lines in source |
| `extraction_status` | string | ✓ | "success", "low_confidence", "unsupported_format" |
| `heading_path` | [string] | Markdown, DOCX only | ["Chapter 1", "Section 2.1"] hierarchy |
| `printed_page` | string or int | PDF only | PDF metadata label, e.g. "v-3" or 7 |

### Future enhancements (Phase 2–3)

These fields are planned but not yet implemented:

- `extraction_confidence`: float 0.0–1.0 (for OCR quality)
- `table_structure`: parsed table cells (currently exported as text)
- `code_language`: detected language for code blocks

Use version in metadata to detect which fields are available.

### Usage in learning workflow

Store the full extraction JSON in your learner workspace. The agent can:

1. Build a source map: map chapter materials to block IDs
2. Generate citations: link questions to specific extracted blocks
3. Detect failures: filter blocks where `extraction_status != "success"`
4. Rebuild on demand: if a chapter needs a specific section re-read, fetch it by block_id

Example: Question Q3 is linked to block b5 from source s1 (file_page 7, lines 23–29). 
If the answer is wrong, you can immediately re-show that exact section.

```

**Acceptance Criteria:**
- [ ] JSON schema is documented with field reference table
- [ ] Field availability matrix (which fields for which source types)
- [ ] Usage examples show how to map questions to blocks
- [ ] Marked as Phase 1 implementation with Phase 2–3 planned fields noted
- [ ] Linked from SKILL.md assessment section

---

### 1.4 Update `help-me-learn/SKILL.md` — Add design choice explanations

**Current issue:** SKILL.md says *what* (one question at a time, 3–5 questions per chapter) but not *why*. This looks like prescriptive rules instead of design decisions.

**Changes:** In the "Learning loop" section, add inline annotations:

```markdown
## Learning loop

1. **Map:** ...
2. **Teach:** Present one idea, a concrete example, and one small learner action. 
   Stop for their response before advancing substantially. 
   
   **Design choice:** One idea per turn reduces cognitive load and prevents 
   the learner from jumping ahead to multiple concepts. This is especially 
   useful for learners who struggle with attention or task initiation, but 
   applies to anyone learning something unfamiliar. Adjust to feedback; 
   this is a default, not a rule.

3. **Check:** End each chapter with a numbered set of questions, normally 3–5. 
   Include explanation and application, plus a misconception or transfer 
   question where useful. Present one at a time by default; provide the 
   full list on request. 
   
   **Design choice:** One question per turn prevents later questions priming 
   answers to earlier ones and reduces decision fatigue. Showing the full 
   list upfront is useful for learners who want to plan their time or 
   understand the scope. Both are valid; let the learner choose.

4. **Review:** ...
5. **Continue or pause:** ...
```

Also add a new subsection:

```markdown
## Design principles (not ADHD rules)

These choices reflect learning science and accessibility, 
not a diagnosis or fixed learning style:

- **Tiny task initiation:** One small action before stopping reduces 
  the friction of starting. Works for anyone facing a large topic.
  
- **Spaced retrieval:** Returning to a concept hours or days later, 
  in a different context, improves long-term retention. We support 
  resumable courses and optional delayed-retrieval practice.
  
- **Worked examples + independent practice:** Showing a solution 
  first, then asking the learner to try, balances cognitive load 
  and transfer.
  
- **External progress record:** Visible state (chapters, next action) 
  helps learners who struggle with memory or attention. It also helps 
  anyone returning after a break.

These are evidence-informed defaults. Adjust them to the learner 
and task. See [evidence and adaptation](references/evidence-and-adaptation.md) 
for research notes and limitations.
```

**Acceptance Criteria:**
- [ ] Design choices explained inline in SKILL.md
- [ ] New "Design principles" section added
- [ ] Marked as defaults/suggestions, not requirements
- [ ] Linked to evidence-and-adaptation.md
- [ ] No change to actual behavior, only documentation

---

## Phase 2: State Schema Extension (2–3 hours, Medium priority)

Adds prerequisite modeling to the JSON schema. Backward-compatible (new optional fields).

### 2.1 Update `help-me-learn/references/state-schema.md` — Add prerequisites

**Addition:** In the "Outcome records" section, extend the schema:

Current:
```markdown
Outcome records require `id`, `description`, `status`, and `evidence_attempt_ids`.
```

Change to:
```markdown
Outcome records require `id`, `description`, `status`, and `evidence_attempt_ids`. 
Optionally include `prerequisite_outcome_ids` to model concept dependencies.

Example:
{
  "id": "oc2",
  "description": "Add fractions with unlike denominators",
  "status": "unassessed",
  "evidence_attempt_ids": [],
  "prerequisite_outcome_ids": ["oc0", "oc1"]
}

The outcomes `oc0` and `oc1` must both be assessed as 
`demonstrated-independently` before teaching `oc2`. 
Use `prerequisite_outcome_ids: []` (empty) for chapters with no prerequisites, 
or omit the field entirely (backward-compatible).

### Readiness check logic

Given a chapter, compute readiness:

1. Get all outcomes in the chapter
2. For each outcome with prerequisite_outcome_ids:
   - Check: Are all prerequisites `demonstrated-independently`?
   - If any prerequisite is `unassessed` or `needs-practice`: not ready
3. If all outcomes are ready: chapter is ready
4. If some prerequisites are gaps: offer focused repair or skip ahead at learner request

This is optional logic; the agent can skip it if stateless or if 
the learner prefers to proceed without readiness checks.

### Storing gap repair outcomes

When a learner returns and prerequisite `oc1` is `needs-practice`, 
create a repair question targeting just that outcome. Record it:

{
  "id": "qR1",
  "chapter_id": "ch_repair",
  "outcome_ids": ["oc1"],
  "prompt": "...",
  "kind": "repair"
}

This is optional structure; you can also handle repair 
diagnostically without pre-defining repair questions.
```

**Acceptance Criteria:**
- [ ] `prerequisite_outcome_ids` field added and optional
- [ ] Readiness check logic documented
- [ ] Gap repair strategy explained
- [ ] Example JSON shown
- [ ] Marked backward-compatible (field can be omitted)

---

### 2.2 Extend `help-me-learn/scripts/session_state.py` — Add readiness command

**Purpose:** Programmatically check if a learner is ready for a chapter.

**New command:**

```bash
python scripts/session_state.py readiness "<learner>/state.json" --chapter ch2
```

**Output:**
```json
{
  "chapter_id": "ch2",
  "chapter_title": "Add unlike fractions",
  "readiness": "ready",
  "details": {
    "outcomes": [
      {
        "id": "oc2",
        "description": "Add fractions with unlike denominators",
        "prerequisites": ["oc0", "oc1"],
        "status": {
          "oc0": "demonstrated-independently",
          "oc1": "demonstrated-independently"
        }
      }
    ],
    "gaps": []
  }
}
```

Or, if not ready:
```json
{
  "readiness": "not_ready",
  "gaps": [
    {
      "outcome_id": "oc1",
      "description": "Identify numerator and denominator",
      "current_status": "needs-practice",
      "repair_suggestion": "Review one misconception question from Chapter 1"
    }
  ]
}
```

**Implementation notes:**
- Read the state.json file
- For each outcome in the target chapter, check its prerequisites
- Traverse the prerequisite graph (outcomes can have prerequisites)
- Return readiness status + detailed gap list
- Do not modify state; this is read-only

**Acceptance Criteria:**
- [ ] Command implemented and tested
- [ ] Handles cycles in prerequisite graph (circular deps)
- [ ] Output is JSON; parse cleanly
- [ ] Outputs both `ready` and `not_ready` cases
- [ ] Gap list includes repair suggestions

---

## Phase 3: Integration Clarity & Resilience (2–3 hours, Medium priority)

Documents timeout/retry logic and failure paths for external integrations.

### 3.1 Create `help-me-learn/references/integration-resilience.md`

**Purpose:** Document timeout, retry, and failure-path logic for Excalidraw and Obsidian MCP servers.

**Content:**

```markdown
# Integration resilience: Timeouts, retries, fallbacks

When connecting to external MCP servers (Excalidraw, Obsidian), 
failures happen: network timeouts, service overload, auth issues. 
This guide specifies behavior to prevent hanging or silent data loss.

## Timeout and retry strategy

Apply this uniformly to all MCP operations:

### Single request: 5 second timeout
- Initial request to create diagram, save note, etc.
- If response not received in 5s: abort and move to retry decision

### Retry decision: Check for existing result (2 second timeout)
- Query: "Does this diagram/note already exist?" (short, cheap query)
- Timeout: 2s (tighter, since we're just checking, not creating)
- Outcome:
  - ✓ Exists: use it, report to learner
  - ✓ Does not exist: retry with fresh request (once)
  - ✗ Second timeout: give up, use fallback

### Second attempt (if retry needed): 5 second timeout
- Fresh request with same parameters
- If successful: use result
- If timeout/error: fall back to text

### Max attempts total: 2 creates + 1 existence check

Do not retry more than twice. A hung service should fail fast.

Timeline example:
```
T=0:   Request to create diagram
T=3:   (in flight)
T=5:   Timeout on initial request → try to check for existing result
T=7:   (checking in flight)
T=9:   Timeout on existence check → user has been waiting 9s already
       → Fail fast, use text fallback, show message
```

## Service failure modes and user messaging

### Timeout: "The diagram service is taking too long. I'll explain it in text instead."

Fallback: Use Mermaid, ASCII art, or short text explanation.
Do NOT retry silently or hang the conversation.

### Authentication error: "I don't have permission to save to that vault. Check your connection settings."

Fallback: Ask for manual save location or use text-only mode.
Do NOT retry; auth errors won't fix themselves.

### Not found (404): "The vault or diagram server is not reachable. Check that it's running."

Fallback: Text mode; offer copy-paste instructions.
Do NOT retry immediately; let user restart service.

### Partial failure (note saved, diagram failed):

Report clearly:
"✓ Note saved to Obsidian as 'Chapter 3 notes'  
✗ Diagram failed to save (timeout); displayed in chat but not persisted"

Do NOT claim both succeeded if one failed.

## Excalidraw-specific: Check and update

When requested to edit an existing diagram:

1. Read current scene (2s timeout)
   - If timeout: "Drawing service is slow; showing last known state"
   - If 404: "Drawing not found; creating new one"
2. Merge learner edits into current scene
3. Save updated scene (5s timeout)
4. If save fails: return the merged scene to learner as text for manual save

Do NOT overwrite an existing diagram based on old local state.

## Obsidian-specific: Atomic note operations

Obsidian does not guarantee atomic writes across multiple notes. 
Use this pattern:

1. Write primary note (e.g., answer review) → wait for response
2. If success: write secondary notes (e.g., links in Start.md)
3. If primary fails: stop; do NOT write secondary
4. If primary succeeds but secondary fails: 
   - Report: "Review saved. Vault link could not be added; saved at [path]"
   - Do NOT retry secondary with initial timeout; just report failure

## State preservation during failures

If saving state to local file + notes to Obsidian:

1. Save state to local JSON first (atomic, fast)
2. Wait for confirmation
3. Then attempt Obsidian writes
4. If Obsidian fails: state is still saved locally; report error and location

Never leave state unsaved to pursue Obsidian persistence.

## User expectations and transparency

Always report:
- ✓ What succeeded (with location/ID if relevant)
- ✗ What failed (with reason: timeout, auth, service error)
- ? What wasn't attempted (e.g., "diagram not saved because timeout occurred")

Example: "Chapter notes saved to Obsidian. Diagram timed out (5s); shown in chat but not persisted. Next steps saved locally."

Do not hide failures; learner needs to know what they can depend on.
```

**Acceptance Criteria:**
- [ ] Timeout values specified (5s request, 2s check, no 3+ retries)
- [ ] Per-failure messaging documented
- [ ] Obsidian atomic-write pattern specified
- [ ] State is saved before integration attempts
- [ ] Fallback paths for Excalidraw and Obsidian
- [ ] Example timeline and messaging included

---

### 3.2 Update `help-me-learn/references/excalidraw.md` and `obsidian.md`

**For excalidraw.md:** Add at end of "Capability check" section:

```markdown
## Timeouts and failure paths

See [integration resilience](integration-resilience.md) for unified 
timeout/retry strategy. Summary for drawings:

- Create diagram: 5s timeout, retry once with existence check
- Update existing diagram: read scene (2s timeout), merge, save (5s timeout)
- If timeout: use ASCII or Mermaid fallback, marked as unsaved

Do not let a hung drawing service delay the lesson.
```

**For obsidian.md:** Add at end of "Failure path" section:

```markdown
## Timeouts and atomic writes

See [integration resilience](integration-resilience.md) for unified 
timeout/retry strategy. Summary for Obsidian:

- Write primary note (answer review, course home): 5s timeout
- If successful, write secondary notes (links, summaries): 5s timeout each
- If primary fails: stop; do not write secondaries
- If secondary fails: report which secondary; primary already saved

Never retry Obsidian writes; auth and availability issues persist. 
Report clearly and continue the lesson.
```

**Acceptance Criteria:**
- [ ] Both files link to integration-resilience.md
- [ ] Summary of timeout strategy in each
- [ ] Specific to drawing/note operations

---

## Phase 4: Python Helper Enhancements (3–4 hours, Lower priority)

Optional but unlocks automation. Do if time permits.

### 4.1 Extend `extract_resource.py` — Add heading extraction

**Current:** Extracts text + page numbers.  
**Enhancement:** For Markdown and DOCX, extract heading hierarchy.

**Implementation:**

```python
def extract_markdown(file_path: str) -> List[Dict]:
    blocks = []
    heading_stack = []  # Track nesting: ["Chapter 1", "Section 2"]
    
    with open(file_path) as f:
        for line_num, line in enumerate(f, 1):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                heading_text = line.lstrip('# ').strip()
                
                # Maintain stack based on level
                heading_stack = heading_stack[:level-1]  # Pop deeper levels
                heading_stack.append(heading_text)
                
                blocks.append({
                    "block_id": f"b{len(blocks)}",
                    "type": "heading",
                    "content": heading_text,
                    "heading_path": heading_stack.copy(),
                    "heading_level": level,
                    "line_range": [line_num, line_num],
                    "extraction_status": "success"
                })
            elif line.strip():
                # Paragraph block
                blocks.append({
                    "block_id": f"b{len(blocks)}",
                    "type": "paragraph",
                    "content": line.strip(),
                    "heading_path": heading_stack.copy(),
                    "line_range": [line_num, line_num],
                    "extraction_status": "success"
                })
    return blocks
```

For DOCX, use python-docx's paragraph style (`paragraph.style.name`) to infer heading level.

**Testing:**
- Extract sample Markdown file, verify heading_path is correct
- Extract sample DOCX, verify heading hierarchy respected

**Acceptance Criteria:**
- [ ] Markdown heading extraction preserves nesting
- [ ] DOCX heading detection works (read style.name)
- [ ] heading_path is a list, empty for paragraphs not under a heading
- [ ] Tests pass for sample files

---

### 4.2 Extend `session_state.py` — Add `repair` command

**Purpose:** Generate suggested repair questions for gaps.

**New command:**

```bash
python scripts/session_state.py repair "<learner>/state.json" --chapter ch2 --generate
```

**Output:**
```json
{
  "chapter_id": "ch2",
  "gaps": [
    {
      "outcome_id": "oc1",
      "description": "Identify numerator and denominator",
      "status": "needs-practice",
      "suggested_repair_question": {
        "id": "qR1_generated",
        "type": "explanation",
        "prompt": "In the fraction 5/8, which number is the numerator?",
        "kind": "repair"
      }
    }
  ]
}
```

Agent can then:
1. Display the repair question
2. Collect answer
3. Create an attempt record with `kind: "repair"`
4. Link evidence to the original outcome

**Implementation notes:**
- Read state.json
- Find outcomes with `status: "needs-practice"`
- For each gap outcome, generate a generic question (simple, one angle)
- Return as JSON; agent decides whether to use it

**Acceptance Criteria:**
- [ ] Command parses chapter_id, outputs JSON
- [ ] Generated questions are generic but aligned to outcome description
- [ ] Questions are marked `kind: "repair"` so they don't overwrite independent evidence
- [ ] Agent can choose to use or skip the generated question

---

## Summary: What's Produced

| Phase | What | Effort | Impact |
|-------|------|--------|--------|
| **1.1** | assessment-generation.md | 2 hrs | Unblock question generation; enable pattern reuse |
| **1.2** | Update obsidian.md (canonical source) | 1 hr | Prevent sync confusion; clarify truth source |
| **1.3** | Update state-schema.md (extraction format) | 1 hr | Document Phase 1 extraction; roadmap Phase 2–3 |
| **1.4** | Update SKILL.md (design choices) | 30 min | Explain *why* not just *what*; reduce prescriptive feeling |
| **2.1** | Extend schema (prerequisites) | 1 hr | Enable readiness checks; model concept dependencies |
| **2.2** | Add `readiness` command to session_state.py | 2 hrs | Programmatic gap detection; guide repair strategy |
| **3.1** | Create integration-resilience.md | 1.5 hrs | Timeout/retry/fallback strategy; prevent hangs |
| **3.2** | Link from excalidraw.md + obsidian.md | 30 min | Integrate resilience guidance into tool docs |
| **4.1** | Extract heading_path in extract_resource.py | 2 hrs | Enable citation mapping; link questions to source |
| **4.2** | Add `repair` command to session_state.py | 1.5 hrs | Generate repair questions; reduce agent cognitive load |
| | **Total** | **~13.5 hours** | **3 phases** |

---

## Execution Notes

**Order:**
1. **Do Phase 1 first** (docs only; no dependencies; highest ROI)
2. **Then Phase 2** (schema extension; unlocks readiness logic)
3. **Then Phase 3** (integration clarity; non-blocking but high UX impact)
4. **Phase 4 last** (Python enhancements; nice-to-have)

**Testing:**
- Phase 1: No code; validate doc links, cross-references
- Phase 2: Unit test readiness logic with sample state.json files
- Phase 3: Document; no code changes needed
- Phase 4: Unit test extraction + repair generation with sample inputs

**Backward compatibility:**
- Phase 1–3: No schema changes, only additions + docs (safe)
- Phase 2: New optional `prerequisite_outcome_ids` field (schema-compatible)
- Phase 4: No breaking changes; new commands only

---

## How to Use This Prompt

Hand this entire document to your AI model (Claude, GPT, etc.) along with your repo structure, and say:

> "Implement the Phase 1 improvements (documentation only). 
> Each item should be merged into the existing skill as a new/updated Markdown file. 
> Use the acceptance criteria to verify completeness. 
> Start with 1.1, then 1.2, then 1.3, then 1.4. 
> Return updated files and a summary of what was added."

After Phase 1 is done and merged:

> "Implement Phase 2 (state schema extension). 
> Update state-schema.md and extend session_state.py with the new `readiness` command. 
> Include unit tests. Return updated files and test results."

Etc.

---

## Questions to Clarify Before Starting

Ask your AI model these before they begin:

1. **For Phase 1.1 (assessment-generation.md):** "Review the existing assessment.md. What domains/patterns does it already cover? Where should generation patterns fit without duplication?"

2. **For Phase 2.2 (readiness command):** "What's the intended behavior if a prerequisite is `demonstrated-with-help` but not independent? Should we block or allow with a warning?"

3. **For Phase 4.1 (heading extraction):** "Should we split heading blocks from paragraph blocks (as shown), or combine them? What's most useful for agent citation?"

These prevent rework.
