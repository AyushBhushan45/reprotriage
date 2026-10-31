# ReproTriage

**Reproduction-first triage for open-source maintainers — in one GitHub Action.**

Maintainers are drowning. LF Research (Oct 2026) estimates 25% of incoming PRs are low-quality "AI slop" — 31% in large projects — and 59% of maintainers report growing volume. The bottleneck is not writing code. It is *verifying* issues and PRs.

ReproTriage helps maintainers decide faster, without adding noise:

- ✅ **Issues:** reproduction steps, expected vs actual, environment/version, minimal example, logs
- ✅ **PRs:** linked issue, tests touched, real description, reviewable size, breaking-change note
- ✅ Posts **one** explainable report comment — re-runs *update the same comment*, no spam
- ✅ **Never auto-closes or auto-rejects** — the maintainer stays the gatekeeper
- ✅ **No API key, no external service.** Stdlib-only Python, runs in *your* repo's own Actions runner, calls only `api.github.com`
- ✅ Optional labels, optional config, possible-duplicate hints, dry-run mode to trial it safely
- ✅ Smart about real life: docs-only PRs don't get nagged for tests

## Install

```yaml
# .github/workflows/reprotriage.yml
name: ReproTriage
on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]
permissions:
  issues: write
  pull-requests: write
jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: AyushBhushan45/reprotriage@v1
        with:
          mode: report-only   # or: label
```

> Live at https://github.com/AyushBhushan45/reprotriage

## Try it locally in 10 seconds

```bash
git clone <this repo>
cd reprotriage
python3 examples/demo.py
# bad issue -> 0/100, good issue -> 100/100, PR without tests -> flagged
python3 -m pytest tests/ -q   # 13 tests
```

Dry-run a real event payload:
```bash
GITHUB_EVENT_PATH=/path/to/event.json INPUT_DRY_RUN=true python3 src/main.py
```

## Optional config — `.github/reprotriage.yml`

```yaml
min_pr_description_chars: 80
max_pr_files: 30
require_linked_issue: true
require_tests: true
```

## Why not just use a code-review bot?

Code-review bots review *code*. ReproTriage checks *readiness before review*: is this issue reproducible? Is this PR linked, tested, and described well enough to spend maintainer time on? That verification step is where maintainer hours disappear. It also never tries to guess "was this written by AI?" — that detection is unreliable and hostile to contributors. Readiness is checkable. Provenance isn't.

## Roadmap

- **v1 (now):** deterministic checks, real Action with comment + labels, config, duplicates hint, dry-run, 13 tests
- **v1.5:** optional BYO-OpenAI-key layer — label classification, specific missing-info request, 5-line PR review brief
- **v2:** opt-in reproduction run in the adopting repo's own Actions sandbox, with an evidence log

## Contributing

Good first issues and design-partner repos are welcome. See `CONTRIBUTING.md`. Please open an issue before a large PR.

## License

MIT — see `LICENSE`.

---
Built in public by Ayush Bhushan. Goal: a real tool real maintainers use — and, over 6-12 months of honest adoption and maintenance, a credible application to OpenAI's Codex for Open Source program.
