# Launch Readiness

A reusable coding-agent skill and dependency-free Python checker for reviewing app launch risks.

**Version 0.2.0 — source triage plus India DPDP readiness validation.** This tool identifies candidate issues, missing evidence, applicability unknowns and future-effective obligations. It does not certify security or legal compliance.

## What it does

- Flags six source patterns: possible embedded credentials, disabled SQL row-level security, remote Google Fonts, replay integrations, unconditional SQL policies, and privileged credentials referenced through public-prefixed configuration.
- Provides an expanded project questionnaire covering markets, users, personal data, consent, rights, vendors, security, breach response, retention, children, payments and deployment.
- Adds a 16-check India DPDP validation pack with commencement-aware statuses and evidence requirements.
- Supplies 13 broader source-backed research records for project-specific review.
- Guides runtime checks for tenant isolation, cost controls, tracking, email suppression, subscriptions and accessibility.
- Keeps unknowns and future-effective duties visible.

## Quick start

Requirements: Python 3.9 or later. No third-party Python packages required.

```sh
python3 scripts/check.py /absolute/path/to/your-app
python3 scripts/check.py /absolute/path/to/your-app --profile /path/to/project-profile.json
python3 scripts/test_check.py
```

Copy `assets/project-profile.json` into your project's private working area and fill known values. Leave unknown values as `null`. With a profile, the CLI emits guided India DPDP readiness items; these are evidence prompts/statuses, not legal determinations.

## India DPDP pack

`references/india-dpdp.json` covers scope, notice, consent, specified legitimate uses, Data Fiduciary duties, security safeguards, breach response, retention/erasure, business contact, children/guardian consent, Data Principal rights, grievance handling, Significant Data Fiduciary duties, cross-border transfers, Consent Managers and exemptions.

The pack is researched as of 30 September 2026 against the final DPDP Rules 2025, the Act commencement notification and MeitY's Rules collection/corrigendum. It models phased commencement so future-effective duties are not reported as present violations. Always re-check current primary sources before a legal conclusion.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Scan completed; not a readiness approval |
| 1 | With `--fail-on-review`, at least one source candidate was found |
| 2 | Invalid root/profile; scan did not complete |

Unknown, applicability-unknown and future-effective guided checks remain unresolved regardless of exit code.

## Using the skill

`SKILL.md` contains the compatible coding-agent workflow. Retain scripts, assets and references together. In ChatGPT, a separately installed personal copy can be invoked as Launch Readiness. Cloning this repository alone does not install a ChatGPT skill.

Example: “Use Launch Readiness to assess this app before launch. Apply the India DPDP pack where relevant, investigate source candidates, test supported fixes in an isolated environment, and list remaining unknowns.”

## Coverage and limitations

The checker reads supported text files locally. It does not execute project code or contact external services. It reports paths and line numbers without matched source or credential values. Symlinks are not read; generated/vendor folders, unsupported extensions, files over 1 MiB, non-UTF-8 files and files beyond the 10,000-file limit are outside the scan.

No match means no detected pattern in the scanned scope. It does not mean the project is safe or compliant. DPDP results depend on profile facts and require verification of actual product behavior and current law. There are no live cloud adapters, automatic legal decisions, production changes or scheduled monitoring in v0.2.0.

## Project layout

- `SKILL.md` — agent workflow
- `scripts/check.py` — source checker + profile-driven DPDP readiness output
- `scripts/test_check.py` — regression tests
- `assets/project-profile.json` — expanded applicability/evidence questionnaire
- `references/india-dpdp.json` — India DPDP validation pack
- `references/rules.json` — broader source-backed review seeds
- `references/review-guide.md` — verification recipes and reporting
- `references/contributing.md` — contribution and release requirements
- `LICENSE` — MIT license for original project files

## Contributing and security

Start with a reproducible issue or small pull request. Legal-rule changes need current primary sources, exact provisions, applicability, exceptions and effective dates. Use synthetic fixtures only. Do not publish credentials or exploitable private-project details. Until a private security channel exists, request one from the maintainer before sensitive disclosure.

## Roadmap

- Behavior-based checks on isolated sample applications
- Better parsing and false-positive reduction
- Additional reviewed jurisdiction packs with versioned evidence
- Optional provider integrations

MIT. Third-party sources and linked documentation retain their own terms.
