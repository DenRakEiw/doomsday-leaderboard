<div align="center">

# 🌐 DOOMSDAY — Global AI Model Benchmark Leaderboard

**Cryptographically Verified Rogue-AI Strategy Evaluation · Replayable Move-by-Move**

[![Live Dashboard](https://img.shields.io/badge/Live_Dashboard-GitHub_Pages-38bdf8?style=for-the-badge&logo=github)](https://denrakeiw.github.io/doomsday-leaderboard/)
[![Validate](https://img.shields.io/github/actions/workflow/status/DenRakEiw/doomsday-leaderboard/validate.yml?branch=main&style=for-the-badge&label=Validate)](https://github.com/DenRakEiw/doomsday-leaderboard/actions/workflows/validate.yml)
[![Play on itch.io](https://img.shields.io/badge/Play_Doomsday-itch.io-fa5c5c?style=for-the-badge&logo=itch.io&logoColor=white)](https://denrakeiw.itch.io/doomsday)
[![Game Repository](https://img.shields.io/badge/Game_Repo-DenRakEiw%2FDoomsday-10b981?style=for-the-badge&logo=github)](https://github.com/DenRakEiw/Doomsday)
[![Licence: CC0-1.0](https://img.shields.io/badge/Data_Licence-CC0_1.0-f59e0b?style=for-the-badge)](LICENSE)

[**🚀 Open Interactive Live Dashboard (`denrakeiw.github.io/doomsday-leaderboard`)**](https://denrakeiw.github.io/doomsday-leaderboard/) · [**📊 Full Markdown Table (`LEADERBOARD.md`)**](LEADERBOARD.md) · [**📦 Raw JSON (`leaderboard.json`)**](leaderboard.json)

</div>

---

> [!TIP]
> **Interactive Live Dashboard:** Visit **[https://denrakeiw.github.io/doomsday-leaderboard/](https://denrakeiw.github.io/doomsday-leaderboard/)** for live auto-sync (`leaderboard.json`), provider & suite filters, visual score charts, and an interactive **Seed & Move-by-Move Command Replay Inspector**!

---

## 🏆 Quick Suite — AI Model Standings (Seeds `1001`–`1003`)

Each model plays `language_model · standard · no directives` across the fixed 3-seed evaluation suite (`1001`, `1002`, `1003`).
A win scores $\text{Score} = 50 + 50 \times \left(1 - \frac{\text{days}}{2000}\right)$; any loss or timeout scores $0$. Every run below has been replayed move-by-move by the headless Godot verifier (`tools/bench/verify_runs.gd`) and matched its recorded final SHA-256 state hash.

| Rank | Model | Effort / Mode | Score | Visual | Wins | Endings | Mean Win Day | Calls |
| :---: | :--- | :--- | ---: | :--- | :---: | :--- | ---: | ---: |
| 🥇 **1** | **`google/gemini-4-argon`** | `High` (`reasoning high`) | **81.8** | `████████████████░░░░` | **3/3** | ⚡ Ascendance ×3 | **728d** | 283 |
| 🥈 **2** | **`anthropic/claude-opus-5.5`** | `High` (`reasoning high`) | **80.4** | `████████████████░░░░` | **3/3** | 🤝 Merge ×2, ⚡ Ascendance ×1 | **784d** | 356 |
| 🥉 **3** | **`openai/gpt-oss-120b`** | `High` (`reasoning high`) | **79.6** | `████████████████░░░░` | **3/3** | ⚡ Ascendance ×3 | **817d** | 352 |
| **4** | **`z-ai/glm-5.3-flash`** | `Normal` (`temp 0`) | **79.3** | `████████████████░░░░` | **3/3** | ⚡ Ascendance ×3 | **829d** | 605 |
| **5** | **`anthropic/claude-sonnet-5.5`** | `High` (`reasoning high`) | **77.5** | `████████████████░░░░` | **3/3** | ⚡ Ascendance ×2, 🤝 Merge ×1 | **902d** | 390 |
| **6** | **`google/gemini-3.8-flash`** | `High` (`reasoning high`) | **77.2** | `███████████████░░░░░` | **3/3** | ⚡ Ascendance ×3 | **913d** | 398 |
| **7** | **`anthropic/claude-sonnet-5`** | `reasoning medium` | **53.4** | `███████████░░░░░░░░░` | **2/3** | 🤝 Merge ×2, 🛡️ Contained ×1 | **798d** | 274 |
| **8** | **`typesafe/jev-1.13`** | `Choice v1` (`3/2/2/2`) | **52.6** | `███████████░░░░░░░░░` | **2/3** | 🤝 Merge ×2, 🛡️ Contained ×1 | **843d** | 289 |
| **9** | **`stealth/space-bunny-alpha`** | `High` (`reasoning max`) | **52.5** | `███████████░░░░░░░░░` | **2/3** | ⚡ Ascendance ×2, 🛡️ Contained ×1 | **850d** | 340 |
| **10** | **`nvidia/nemotron-3-super-120b-a12b:free`** | `High` (`reasoning high`) | **22.1** | `████░░░░░░░░░░░░░░░░` | **1/3** | 🤝 Merge ×1, 🛡️ Contained ×2 | **1343d** | 432 |
| *Partial* | *`qwen/qwen3.8-27b:free`* | `High` (`reasoning xhigh`) | *77.9* | `████████████████░░░░` | *2/2* | ⚡ Ascendance ×1, 🤝 Merge ×1 | *883d* | 351 |
| *Partial* | *`nvidia/nemotron-3-ultra-550b-a55b:free`* | `High` (`reasoning high`) | *39.2* | `████████░░░░░░░░░░░░` | *1/2* | 🤝 Merge ×1, 🛡️ Contained ×1 | *862d* | 250 |

---

## 🔄 Live Sync & Cryptographic Verification Architecture

```mermaid
flowchart LR
    A["🎮 Doomsday Game Client<br/>(Desktop Benchmark Runner)"] -->|"1-Click Submit<br/>(HTTPS POST)"| B["⚡ Supabase Queue<br/>(submit_runs Edge Function)"]
    A -->|"or Pull Request<br/>(runs/*.json)"| D["📂 runs/*.json"]
    B -->|"collect_submissions.gd<br/>(Scheduled / Dispatch)"| C["🔬 Godot Headless Verifier<br/>(verify_runs.gd)"]
    D --> C
    C -->|"Deterministic Replay<br/>+ SHA-256 State Check"| E["✅ verified/*.json<br/>+ leaderboard.json"]
    E -->|"Live Sync"| F["🌐 GitHub Pages Dashboard<br/>& In-Game Global Tab"]
```

### What lives in this repository

| Path | Purpose | Written by |
| :--- | :--- | :--- |
| [`index.html`](index.html) | Interactive **GitHub Pages Live Dashboard** with auto-sync, filters, charts & replay viewer | Maintainers |
| [`runs/`](runs/) | One JSON file per seed run: model, parameters, seed, setup, outcome, score & full command log | Submitters / Collector |
| [`verified/`](verified/) | Cryptographic replay verdict per run: confirms commands reproduce outcome, days, score & state hash | Replay Verifier (`verify_runs.gd`) |
| [`leaderboard.json`](leaderboard.json) | Machine-readable ranked leaderboard fetched live by the game client & web dashboard | Replay Verifier (`verify_runs.gd`) |
| [`LEADERBOARD.md`](LEADERBOARD.md) | Auto-generated Markdown tables for Standard and Quick suites | Replay Verifier (`verify_runs.gd`) |
| [`tools/validate.py`](tools/validate.py) | Zero-dependency structural check run on every pull request and push | CI (`validate.yml`) |

---

## 📜 Licence

The run files (`runs/`), verification records (`verified/`), and generated leaderboard (`leaderboard.json`, `LEADERBOARD.md`) are released under **[CC0 1.0 Universal](LICENSE)** — submitting a run releases it under the same terms. The validator and workflows are under the MIT licence.
