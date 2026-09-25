# Doomsday — model benchmark leaderboard

*Doomsday* is a strategy game in which the player is a rogue AI. Its benchmark mode lets a
language model play the game over a fixed suite of seeds; this repository is the **global
leaderboard** of those runs. The game reads `leaderboard.json` from here when a player opens its
benchmark list, and can replay any listed run move by move.

## What is here

| Path | What | Written by |
| --- | --- | --- |
| `runs/` | One JSON file per run: model, parameters, seed, setup, outcome, score and the full command list | submitters (pull request) |
| `verified/` | One record per run: did its commands reproduce its outcome, days, score and final state hash? | the replay verifier |
| `leaderboard.json` | The ranked rows the game downloads — **verified runs only** | the replay verifier |
| `LEADERBOARD.md` | The same table for people | the replay verifier |
| `tools/validate.py` | The structural check every pull request runs | — |

## How a run gets on the board

1. Play the benchmark suite with the game's benchmark tool. It writes one file per seed, named
   `<model-slug>__<params-id>__p<prompt-version>__<suite>__s<seed>.json`.
2. Open a pull request that adds those files under `runs/` — nothing else. The `validate`
   check must pass: one file per run, well-formed JSON, the file name matching its contents, at
   most 20 runs and 4 MB per file.
3. After the merge the **replay verifier** plays every new run again from its seed and its
   commands with the game version the run names. A run whose outcome, days, score or final
   state hash differ is marked rejected, with the reason, in `verified/`. Only verified runs are
   counted.

The verifier proves that a score is real — that these commands, on this game version, win on
this day. It cannot prove *which* model chose the commands; the model name is the submitter's
claim.

## How the game reads it

The game fetches

    https://raw.githubusercontent.com/DenRakEiw/doomsday-leaderboard/main/leaderboard.json

only when the player opens the benchmark list, sends nothing, and falls back to its last copy
(or the list it shipped with) when offline. The file's format is `version: 1`: `generated`,
`content_hash` (the game content the current rows were played on) and `rows`, one per model,
parameter set, prompt version, locale and suite, with the mean score, wins, outcomes and the run
files it counts.

## Scoring

A win scores 50 plus up to 50 for speed (`50 + 50 × (1 − days / max_days)`); any other outcome
scores 0. A row's score is the mean over its runs; a row is *complete* when it has a run for
every seed of its suite. Rows played on older game content are listed below the current ones.

## Licence

The run files, verification records and generated leaderboard are released under
[CC0 1.0](LICENSE) — submitting a run releases it the same way. The validator and workflows are
under the MIT licence (`tools/LICENSE`).
