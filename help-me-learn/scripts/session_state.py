"""Validate and atomically save explicit, versioned learner-state files."""

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import tempfile


STATUSES = {"unassessed", "needs-practice", "demonstrated-with-help", "demonstrated-independently"}
PHASES = {"intake", "learning", "assessment", "review", "paused", "complete"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def string(value, where, nonempty=False):
    require(isinstance(value, str), f"{where} must be a string")
    require(not nonempty or bool(value.strip()), f"{where} must not be empty")


def fields(obj, names, where):
    require(isinstance(obj, dict), f"{where} must be an object")
    require(set(names) <= obj.keys(), f"{where} missing fields: {sorted(set(names) - obj.keys())}")


def records(items, where):
    require(isinstance(items, list), f"{where} must be a list")
    result = {}
    for item in items:
        fields(item, ["id"], where)
        string(item["id"], f"{where}.id", True)
        require(item["id"] not in result, f"duplicate {where} id: {item['id']}")
        result[item["id"]] = item
    return result


def validate(state):
    fields(state, ["schema_version", "revision", "topic", "goal", "language", "position",
                   "sources", "chapters", "questions", "attempts", "preferences", "next_action"], "state")
    require(type(state["schema_version"]) is int and state["schema_version"] == 1,
            "unsupported schema_version; preserve the file and migrate explicitly")
    require(type(state["revision"]) is int and state["revision"] >= 0, "revision must be a nonnegative integer")
    for key in ("topic", "goal", "language", "next_action"):
        string(state[key], key)
    require(isinstance(state["preferences"], dict), "preferences must be an object")
    for key, value in state["preferences"].items():
        string(value, f"preferences.{key}")

    sources = records(state["sources"], "sources")
    for source in sources.values():
        fields(source, ["title", "location", "status", "locators", "limitations"], "source")
        for key in ("title", "location", "limitations"):
            string(source[key], f"source.{key}")
        require(source["status"] in ("listed", "partial", "read", "unavailable"), "invalid source status")
        require(isinstance(source["locators"], list), "source.locators must be a list")
        for locator in source["locators"]:
            string(locator, "source locator", True)

    chapters = records(state["chapters"], "chapters")
    all_outcomes = {}
    units_by_chapter = {}
    for cid, chapter in chapters.items():
        fields(chapter, ["title", "source_ids", "units", "outcomes"], "chapter")
        string(chapter["title"], "chapter.title", True)
        require(isinstance(chapter["source_ids"], list), "chapter.source_ids must be a list")
        for sid in chapter["source_ids"]:
            require(isinstance(sid, str) and sid in sources, f"unknown source: {sid}")
        units = records(chapter["units"], "units")
        for unit in units.values():
            fields(unit, ["title"], "unit")
            string(unit["title"], "unit.title", True)
        units_by_chapter[cid] = units
        for oid, outcome in records(chapter["outcomes"], "outcomes").items():
            require(oid not in all_outcomes, f"outcome id must be globally unique: {oid}")
            fields(outcome, ["description", "status", "evidence_attempt_ids"], "outcome")
            string(outcome["description"], "outcome.description", True)
            require(isinstance(outcome["status"], str) and outcome["status"] in STATUSES, "invalid outcome status")
            require(isinstance(outcome["evidence_attempt_ids"], list), "evidence_attempt_ids must be a list")
            all_outcomes[oid] = (cid, outcome)

    questions = records(state["questions"], "questions")
    for question in questions.values():
        fields(question, ["chapter_id", "outcome_ids", "prompt"], "question")
        cid = question["chapter_id"]
        require(isinstance(cid, str) and cid in chapters, "unknown question chapter")
        string(question["prompt"], "question.prompt", True)
        require(isinstance(question["outcome_ids"], list) and question["outcome_ids"], "question needs outcome_ids")
        for oid in question["outcome_ids"]:
            require(isinstance(oid, str) and oid in all_outcomes and all_outcomes[oid][0] == cid,
                    f"question outcome not in its chapter: {oid}")

    attempts = records(state["attempts"], "attempts")
    for attempt in attempts.values():
        fields(attempt, ["question_id", "answer", "assistance", "feedback", "kind"], "attempt")
        qid = attempt["question_id"]
        require(isinstance(qid, str) and qid in questions, "unknown attempt question")
        for key in ("answer", "feedback"):
            string(attempt[key], f"attempt.{key}")
        require(attempt["assistance"] in ("none", "hint", "solution"), "invalid assistance")
        require(attempt["kind"] in ("practice", "chapter-check", "retry", "delayed-retrieval"), "invalid attempt kind")
        if attempt["kind"] == "delayed-retrieval":
            from datetime import date
            string(attempt.get("date"), "delayed-retrieval.date", True)
            date.fromisoformat(attempt["date"])

    for oid, (_, outcome) in all_outcomes.items():
        evidence = outcome["evidence_attempt_ids"]
        for aid in evidence:
            require(isinstance(aid, str) and aid in attempts, f"unknown evidence attempt: {aid}")
            require(oid in questions[attempts[aid]["question_id"]]["outcome_ids"], "evidence does not assess this outcome")
        if outcome["status"] != "unassessed":
            require(bool(evidence), "assessed outcome requires evidence")
        if outcome["status"] == "demonstrated-independently":
            require(any(attempts[aid]["assistance"] == "none" for aid in evidence),
                    "independent outcome needs at least one unassisted attempt")

    position = state["position"]
    fields(position, ["chapter_id", "unit_id", "phase", "question_id"], "position")
    require(isinstance(position["phase"], str) and position["phase"] in PHASES, "invalid position.phase")
    cid, uid, qid = (position[k] for k in ("chapter_id", "unit_id", "question_id"))
    require(cid is None or isinstance(cid, str) and cid in chapters, "unknown position chapter")
    require(uid is None or isinstance(uid, str) and cid is not None and uid in units_by_chapter[cid], "unknown position unit")
    require(qid is None or isinstance(qid, str) and qid in questions and questions[qid]["chapter_id"] == cid,
            "position question does not belong to current chapter")
    if "assistance" in position:
        require(position["assistance"] in ("none", "hint", "solution"), "invalid position assistance")
    if "hints" in position:
        require(isinstance(position["hints"], list), "position.hints must be a list")
        for hint in position["hints"]:
            string(hint, "position hint")
    return state


def reject_constant(value):
    raise ValueError(f"non-JSON numeric constant: {value}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_state(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return validate(json.load(stream, object_pairs_hook=unique_object, parse_constant=reject_constant))


@contextmanager
def file_lock(path):
    lock = path.with_name(path.name + ".lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def atomic_write(path, state):
    validate(state)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix="." + path.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def save_state(path, candidate, initialize=False):
    path = Path(path).resolve()
    validate(candidate)
    with file_lock(path):
        if initialize:
            require(not path.exists(), "state already exists; use show or update")
            require(candidate["revision"] == 0, "initial revision must be 0")
        else:
            current = read_state(path)
            require(candidate["revision"] == current["revision"], "stale revision; reload state and reapply changes")
            # Existing attempts are historical records; corrections belong in new attempts.
            old = {attempt["id"]: attempt for attempt in current["attempts"]}
            new = {attempt["id"]: attempt for attempt in candidate["attempts"]}
            require(all(new.get(aid) == attempt for aid, attempt in old.items()),
                    "existing attempts cannot be removed or changed; append a new attempt")
            assessed_questions = {attempt["question_id"] for attempt in old.values()}
            old_questions = {q["id"]: q for q in current["questions"]}
            new_questions = {q["id"]: q for q in candidate["questions"]}
            require(all(new_questions.get(qid) == old_questions[qid] for qid in assessed_questions),
                    "questions with attempts cannot change; create a fresh question id")
            candidate = dict(candidate, revision=current["revision"] + 1)
        atomic_write(path, candidate)
    return candidate


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "show", "validate", "update"):
        child = sub.add_parser(command)
        child.add_argument("path", type=Path)
        if command == "init":
            child.add_argument("--topic", default="")
            child.add_argument("--goal", default="")
        if command == "update":
            child.add_argument("--from", dest="candidate", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            template = Path(__file__).resolve().parents[1] / "assets" / "session-state.json"
            state = read_state(template)
            state.update(topic=args.topic, goal=args.goal)
            result = save_state(args.path, state, initialize=True)
        elif args.command == "update":
            require(args.path.resolve() != args.candidate.resolve(), "candidate must be a separate file")
            result = save_state(args.path, read_state(args.candidate))
        else:
            result = read_state(args.path)
        print(json.dumps(result if args.command == "show" else {"ok": True, "revision": result["revision"]},
                         ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError) as exc:
        print(f"State error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
