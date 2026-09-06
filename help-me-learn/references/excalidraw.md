# Optional Excalidraw MCP integration

Use when a learner requests Excalidraw or a connected drawing tool can clarify the current concept. It complements the learning loop; it is not required for every chapter.

## Capability check

Discover the actual connected tools. Read the server's format/reference tool before the first drawing call if it provides one; reuse that guidance within the session. Do not invent tool names, input schemas, export operations, or scene-reading capabilities. Distinguish drawing creation, existing-scene editing, image inspection, export, and persistent storage: availability of one does not imply the others.

The [official Excalidraw MCP repository](https://github.com/excalidraw/excalidraw-mcp) documents interactive diagram rendering through MCP Apps, with remote and local options. Inline interaction depends on the host's support. Checked 2026-09-06; consult current server instructions before setup. Configuration belongs to the host, not this skill.

## Timeouts and failure paths

Read [integration resilience](integration-resilience.md) before writes. Where the host supports it, use 5 seconds for creation/saving and 2 seconds for scene reads or existence checks. After an ambiguous creation, at most one checked, safe retry is allowed. No existence check or an operation still in flight means no duplicate create. Read the latest scene before an edit; preserve learner changes. Fall back to text or Mermaid with accurate saved/unsaved/unknown status.

## Draw for a learning outcome

1. Identify the relationship to explain: sequence, comparison, hierarchy, or cause and effect. Use the inspected source or label the drawing as a conceptual example.
2. Start with one small, readable scene, normally 3–5 major ideas. This is a flexible design default. Use short labels, clear arrow direction, generous space, and color with a consistent meaning. Avoid decorative movement; prefer a stable viewport when animation distracts the learner.
3. Follow the connected server's current element schema. Maintain unique element IDs and retain returned scene/checkpoint IDs for supported edits. Inspect the rendered result when the host allows it; check clipping, text contrast, arrow labels, and source accuracy. If inspection is unavailable, disclose that visual QA is incomplete.
4. Explain the diagram in a few sentences, then ask one prediction or reconstruction question. During assessment, do not draw the solution before the learner attempts the problem unless they request help. Record a solution-revealing diagram as assistance.

For numeric charts and simulations, follow [resources and visuals](resources-and-visuals.md). A drawing is not automatically a functioning simulation; do not claim controls or calculations exist unless implemented and tested.

## Updates and persistence

Read the current scene or restore its latest checkpoint when supported before making a targeted change. Preserve learner edits. If the tool cannot retrieve the current scene, do not overwrite it based on an old local description; create a clearly identified new diagram or request the current export.

A checkpoint identifies tool state; it is not a guaranteed portable file, vault attachment, or durable share link. Only report exported/saved files after the corresponding operation succeeds. Do not rename a raw `.excalidraw` scene to `.excalidraw.md` and assume it is compatible with an Obsidian plugin.

When saving to Obsidian, follow [Obsidian integration](obsidian.md): use a supported export format, save the actual artifact if attachment writing is available, and link the verified path. If export is unavailable, save the text explanation and an actual returned link if one exists; label the drawing as session-only otherwise. Never fabricate a download or embed target.

## Failure path

If tools are absent, offer Mermaid, ASCII, or a short table. If creation fails, follow the bounded checks and retry policy above; correct an actionable input error only within that total budget. Preserve the intended explanation and do not repeatedly create duplicate scenes.

Only send content needed for the diagram to the configured server. Use previously authorized integration scope; do not upload an entire private PDF simply to draw a concept from one paragraph.
