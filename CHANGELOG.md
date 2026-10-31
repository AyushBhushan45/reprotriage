# Changelog

## v1.0.0 — 2026-10-31
First complete build.
- Deterministic issue readiness: reproduction steps, expected vs actual, environment/version, minimal example, logs
- Deterministic PR readiness: linked issue, tests touched, description length, reviewable size, breaking-change note
- One updatable report comment (re-runs edit the same comment, no spam)
- Optional label mode (`needs-info`, `needs-repro`, `ready-for-review`)
- Optional config at `.github/reprotriage.yml`
- Possible-duplicate title hints for issues
- Dry-run mode for safe trials on a fork
- Docker GitHub Action (`action.yml` + `Dockerfile`), stdlib-only Python, no external services
- Test suite + demo

## v0.1.0 — 2026-10-31
Initial scaffold: core checks, README, roadmap, application draft.
