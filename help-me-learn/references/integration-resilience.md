# Integration resilience: Timeouts, retries, fallbacks

Read before MCP writes or when an Excalidraw/Obsidian operation fails. These are behavioral limits for the agent, not networking code bundled with the skill.

## Time budget and retry decision

Use a **5-second request timeout** and a **2-second read/existence-check timeout** when the host exposes timeout controls. If the host cannot set or cancel timeouts, disclose that limitation when relevant, rely on its actual completion/error, and do not claim the call was aborted at five seconds. Never start a duplicate mutation while the original request may still be in flight.

For a drawing creation: make one request, then at most one bounded existence check after an ambiguous timeout. If the intended result exists and is verified, use it. If it is confirmed absent and the original operation is finished/cancelled or the server supports a documented idempotency key, retry once with the same operation identity. If existence is unknown, the check times out, or no check capability exists, fall back without another create. A timeout does not prove a write failed.

Maximum drawing budget: **2 creates + 1 existence check**, never three creates. Do not bypass these limits by calling a different tool for the same mutation. Authentication/authorization errors get no retry. Honor a server's retry-after signal by falling back for the lesson rather than busy-waiting.

Example with enforceable deadlines:

```text
t=0s  Initial creation starts.
t=5s  Request times out; begin existence check.
t=7s  Check times out; persistence is unknown. Stop and explain in text.
```

If the check instead confirms absence at t=6s and a retry is safe, the second create has a deadline of t=11s. Report actual observed timings, not this illustrative timeline as measured fact.

## Obsidian: sequential writes, no automatic write retries

Obsidian note operations are not a multi-note transaction. Apply the stricter note policy: **one write attempt per note in this operation**. After an ambiguous result, one read-back check may establish success; it is not another write. Do not automatically retry primary or secondary note writes. Offer an explicit later retry or a copyable draft after reporting the result.

1. In JSON mode, confirm the local state save first. If it fails, stop dependent integration writes and retain the new work as a draft.
2. Write the primary note, such as an answer review, with the 5-second timeout where supported. Verify the intended content with a bounded read-back when needed.
3. Only after confirmed success, write secondary links or summaries, one at a time. Stop dependent writes on any failure or unknown result.
4. If the primary succeeded but a summary failed, report each result and the verified primary path. Do not roll back a successful primary or create a duplicate review.

In notes-only mode the primary review may be saved before `Start.md`; if the course-home save then fails, the review is durable but the resume record is stale. Report both states. Never claim an atomic transaction or rollback across notes.

## Drawing edits

Read/restore the latest scene with a 2-second read budget where supported. If unavailable, do not overwrite from an old local view. A missing scene can lead to a clearly identified new diagram only within the learner's request; a stale local description is not a verified current scene.

Merge the requested change while preserving learner edits, then save with a 5-second request budget. Apply the same existence/idempotency safeguards as creation. If confirmation is unavailable, keep the intended change as text and any valid export already obtained, labeled unsaved or unconfirmed. Do not call an element description an exported scene file.

## Failures and useful messages

| Result | Message and next action |
| --- | --- |
| Timeout/unknown completion | “The drawing request timed out; I couldn't confirm whether it saved. Here is the explanation in text.” |
| Authentication/permission failure | “I couldn't save to that vault because the connection was denied. Your draft is below.” Use host settings for credentials; do not retry automatically. |
| Not found | “That note or scene wasn't found.” Check the exact target. A missing note may be expected for creation; a missing endpoint needs connection repair. A 404 alone does not prove the service is offline. |
| Service/network unavailable | “The connection is unavailable. We'll continue in text.” Preserve pending output with its intended destination. |
| Partial success | “Progress saved locally at [actual path]. Review saved at [verified note path]. Course-home update failed; the resume note is stale.” |

## Report what the learner can rely on

Distinguish **confirmed saved**, **confirmed failed**, **unknown**, and **not attempted**. Include a real location/ID when available. Do not say a diagram was displayed if creation failed before rendering, or say “not saved” when a timeout left its result unknown. End with one useful learning action, keeping setup troubleshooting separate from the lesson.

For persistence decisions, follow [canonical source selection](obsidian.md#canonical-source-choose-one). See [Excalidraw](excalidraw.md) and [Obsidian](obsidian.md) for operation-specific capabilities.
