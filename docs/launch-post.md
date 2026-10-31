# Launch drafts — ready the day the repo goes public
Repo: https://github.com/AyushBhushan45/reprotriage (once created)

## X post (copy-paste, under 280 chars with link added separately)
I built ReproTriage: a GitHub Action that checks if an issue is reproducible and if a PR is actually ready for review — linked, tested, described — in one report. No auto-close. No AI guessing. Maintainers stay in charge. Open source, MIT.

## LinkedIn / long form outline
- Hook: 25% of PRs maintainers receive are estimated to be low-quality "AI slop" (LF Research, Oct 2026). The problem is not writing code, it's verifying it.
- What I built: reproduction-first triage — issue completeness + PR readiness, one updatable comment, report-only.
- What it deliberately does NOT do: auto-close, auto-reject, or try to detect "was this written by AI".
- Demo numbers from the built-in example: bad issue 0/100, good issue 100/100.
- Ask: looking for 3-5 design-partner repos. If you maintain an OSS project and triage eats your week, try it in dry-run mode and tell me what's wrong.

## Release notes — v1.0.0
See CHANGELOG.md. Tag `v1.0.0` on the first push commit, then create the GitHub Release from that tag with the CHANGELOG v1.0.0 section as the body.
Also pin: Marketplace listing is a later step (requires a release + verified action metadata) — do not claim it until it exists.
