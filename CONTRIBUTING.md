# Contributing to Launch Readiness

Start with a reproducible issue or a small, independently reviewable pull request: the problem, the scope, a synthetic fixture, the expected result, and the limitations. Use synthetic data only — never commit customer records or real keys.

**Rules and legal content.** The detailed requirements live in `references/contributing.md`. In short: legal-rule changes need the exact primary source and section, applicability, exceptions, effective dates, and a verification date. Legal interpretations require qualified review before being presented as authoritative. Inclusion in this repository is not a certification of anything.

**Detectors.** Add positive, negative, unknown, and relevant exception fixtures. Treat regex signals according to what they actually prove — a pattern match is a candidate, not a violation. Keep default execution network-free, keep output redacted, and never execute project code. Test empty projects, unreadable/oversized files, and symlinks.

**Fixes.** Add before/after behavioral tests and rollback guidance where applicable.

**Tests and release.** Run `python3 scripts/test_check.py` after every change. The release gate: tests pass, scope and limitations are accurate, no unsupported compliance claims, no customer artifacts bundled, contribution and license terms present.

Original project files are MIT licensed. Check third-party licenses individually.
