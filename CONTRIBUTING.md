# Contributing to ReproTriage

Welcome — especially first-time contributors.

1. Open an issue first for anything bigger than a typo fix.
2. Keep the core rule: **report-only by default, never auto-close or auto-reject.**
3. Keep the deterministic layer free and key-less. LLM features must stay optional.
4. Add a test for every new check in `tests/test_triage.py`.
5. Run `python -m pytest tests/ -q` before opening a PR.

Good first issues: new issue/PR checks, better wording for missing-info messages, examples for popular frameworks.
