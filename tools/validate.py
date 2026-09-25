"""Structural check of Doomsday benchmark run files (no game needed).

This is the public half of the leaderboard's checks: it runs on every pull request and on
every push to main, and only answers "is this a well-formed run file in the right place?".
Whether a run is *true* -- whether its commands really reproduce its outcome, days and
state hash -- is decided by the replay verifier, which needs the game and writes
``verified/``. A run without a passing record there never reaches ``leaderboard.json``.

Usage:
    python tools/validate.py --all                    # every file under runs/
    python tools/validate.py --pr --changes FILE      # `git diff --name-status` of a PR
    python tools/validate.py runs/a.json runs/b.json  # the named files

Exit code 0 when everything passes, 1 otherwise. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = "runs"

ENTRY_VERSION = 1
MAX_BYTES = 4_000_000  # the game's BenchLibrary.MAX_BYTES
MAX_FILES_PER_PR = 20
MAX_COMMANDS = 20_000
MAX_DECISIONS = 5_000
MAX_MODEL_LEN = 200
LOCALES = {"en", "de"}

# Paths a pull request may touch. Everything else is written by maintainers or the verifier.
PR_PATH = re.compile(r"^runs/[a-z0-9._-]+\.json$")
PARAMS_ID = re.compile(r"^[0-9a-f]{8}$")
IDENT = re.compile(r"^[a-z0-9_]*$")
MODEL = re.compile(r"^[\x21-\x7e]+$")  # printable ASCII, no spaces

WHOLE = "whole"
NUMBER = "number"
STRING = "string"
BOOL = "bool"
OBJECT = "object"
ARRAY = "array"

# benchmark.md §10.2 -- the keys a BenchEntry writes, and what each holds.
REQUIRED: dict[str, str] = {
    "version": WHOLE,
    "model": STRING,
    "backend": STRING,
    "params": OBJECT,
    "params_id": STRING,
    "prompt_version": WHOLE,
    "parser_version": WHOLE,
    "locale": STRING,
    "suite": STRING,
    "game_version": STRING,
    "content_hash": STRING,
    "seed": WHOLE,
    "setup": OBJECT,
    "max_days": WHOLE,
    "interval_days": WHOLE,
    "recorded": STRING,
    "outcome": STRING,
    "variant": STRING,
    "days": WHOLE,
    "end_day": WHOLE,
    "score": NUMBER,
    "calls": WHOLE,
    "cached_calls": WHOLE,
    "invalid_answers": WHOLE,
    "rejected_actions": WHOLE,
    "tokens_in": WHOLE,
    "tokens_out": WHOLE,
    "cost_usd": NUMBER,
    "budget_exhausted": BOOL,
    "commands": ARRAY,
    "decisions": ARRAY,
}
NON_NEGATIVE = (
    "seed", "days", "end_day", "calls", "cached_calls", "invalid_answers",
    "rejected_actions", "tokens_in", "tokens_out",
)


def _is(value: object, kind: str) -> bool:
    # JSON writers differ on 1001 vs 1001.0, so "whole" is a value check, not a type check
    # (the game's own rule, PROGRESS 2026-09-22 S1.1). bool is excluded: Python treats it as int.
    if kind == WHOLE:
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        return isinstance(value, float) and math.isfinite(value) and value.is_integer()
    if kind == NUMBER:
        return (isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(float(value)))
    if kind == STRING:
        return isinstance(value, str)
    if kind == BOOL:
        return isinstance(value, bool)
    if kind == OBJECT:
        return isinstance(value, dict)
    if kind == ARRAY:
        return isinstance(value, list)
    raise ValueError(kind)


def slug(model: str) -> str:
    """benchmark.md §10.2: lower-case, `/` -> `--`, anything outside [a-z0-9._-] -> `-`."""
    lowered = model.lower().replace("/", "--")
    return re.sub(r"[^a-z0-9._-]", "-", lowered)


def expected_name(entry: dict) -> str:
    return "%s__%s__p%d__%s__s%d.json" % (
        slug(entry["model"]), entry["params_id"], int(entry["prompt_version"]),
        entry["suite"], int(entry["seed"]))


def check_entry(entry: object, file_name: str, from_pr: bool) -> list[str]:
    """Every problem with one parsed run file; an empty list means it passes."""
    if not isinstance(entry, dict):
        return ["the file is not a JSON object"]
    problems: list[str] = []
    for key, kind in REQUIRED.items():
        if key not in entry:
            problems.append("missing key `%s`" % key)
        elif not _is(entry[key], kind):
            problems.append("`%s` must be a %s" % (key, kind))
    if problems:
        return problems  # the checks below assume the types

    if int(entry["version"]) != ENTRY_VERSION:
        problems.append("unknown `version` %s (expected %d)" % (entry["version"], ENTRY_VERSION))
    model = entry["model"]
    if not model or len(model) > MAX_MODEL_LEN or not MODEL.match(model):
        problems.append("`model` must be 1-%d printable characters without spaces" % MAX_MODEL_LEN)
    if model.startswith("bot:") or entry["backend"] == "bot":
        if from_pr:
            problems.append("reference bot rows are written by the verifier, not submitted")
    if not PARAMS_ID.match(entry["params_id"]):
        problems.append("`params_id` must be 8 lower-case hex digits")
    if entry["locale"] not in LOCALES:
        problems.append("`locale` must be one of %s" % sorted(LOCALES))
    if not entry["suite"] or not IDENT.match(entry["suite"]):
        problems.append("`suite` must be a lower-case id")
    if not entry["content_hash"]:
        problems.append("`content_hash` is empty")
    for key in NON_NEGATIVE:
        if entry[key] < 0:
            problems.append("`%s` must not be negative" % key)
    if entry["max_days"] < 1 or entry["interval_days"] < 1:
        problems.append("`max_days` and `interval_days` must be at least 1")
    if not 0.0 <= float(entry["score"]) <= 100.0:
        problems.append("`score` must lie in 0..100")
    if float(entry["cost_usd"]) < 0.0:
        problems.append("`cost_usd` must not be negative")
    if not ("hash" in entry and (isinstance(entry["hash"], str) and entry["hash"]
                                 or _is(entry["hash"], WHOLE))):
        problems.append("missing or empty `hash` (the final state hash)")

    setup = entry["setup"]
    for key, kind in (("architecture", STRING), ("directives", ARRAY),
                      ("difficulty", STRING), ("scenario", STRING)):
        if key not in setup or not _is(setup[key], kind):
            problems.append("`setup.%s` must be a %s" % (key, kind))
    if isinstance(setup.get("directives"), list) and not all(
            isinstance(d, str) for d in setup["directives"]):
        problems.append("`setup.directives` must hold ids")

    commands = entry["commands"]
    if len(commands) > MAX_COMMANDS:
        problems.append("more than %d commands" % MAX_COMMANDS)
    last_day = 0
    for i, command in enumerate(commands):
        if not isinstance(command, dict) or not isinstance(command.get("type"), str) \
                or not _is(command.get("day"), WHOLE):
            problems.append("command %d needs a string `type` and a whole `day`" % i)
            break
        day = int(command["day"])
        if day < last_day or day > int(entry["end_day"]):
            problems.append("command %d is out of order or after the run's end" % i)
            break
        last_day = day
    if len(entry["decisions"]) > MAX_DECISIONS:
        problems.append("more than %d decisions" % MAX_DECISIONS)
    if not all(isinstance(d, dict) for d in entry["decisions"]):
        problems.append("every decision must be an object")

    if not problems and file_name != expected_name(entry):
        problems.append("file name must be `%s`" % expected_name(entry))
    return problems


def check_file(path: Path, from_pr: bool) -> list[str]:
    size = path.stat().st_size
    if size > MAX_BYTES:
        return ["file is %d bytes, above the %d limit" % (size, MAX_BYTES)]
    try:
        entry = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return ["not valid UTF-8 JSON: %s" % error]
    return check_entry(entry, path.name, from_pr)


def changed_paths(changes_file: Path) -> tuple[list[str], list[str]]:
    """(paths to check, problems) from `git diff --name-status --no-renames` output."""
    paths: list[str] = []
    problems: list[str] = []
    for line in changes_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        status, _, path = line.partition("\t")
        if not PR_PATH.match(path):
            problems.append("%s: a pull request may only add or change `runs/*.json`" % path)
        elif status not in ("A", "M"):
            problems.append("%s: a pull request may not delete a run (status %s)" % (path, status))
        else:
            paths.append(path)
    if len(paths) > MAX_FILES_PER_PR:
        problems.append("%d runs in one pull request (at most %d)" % (len(paths), MAX_FILES_PER_PR))
    return paths, problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*")
    parser.add_argument("--all", action="store_true", help="check every file under runs/")
    parser.add_argument("--pr", action="store_true", help="apply the pull-request rules")
    parser.add_argument("--changes", type=Path, help="git diff --name-status output")
    args = parser.parse_args(argv)

    problems: list[str] = []
    paths: list[str] = list(args.files)
    if args.changes:
        more, problems = changed_paths(args.changes)
        paths += more
    if args.all:
        paths += sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / RUNS_DIR).glob("*.json"))

    for rel in paths:
        for problem in check_file(ROOT / rel, args.pr):
            problems.append("%s: %s" % (rel, problem))

    for problem in problems:
        print("::error::%s" % problem if "GITHUB_ACTIONS" in __import__("os").environ else problem)
    print("validate: %d file(s), %d problem(s)" % (len(paths), len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
