# Launch Readiness

A reusable coding-agent skill and dependency-free Python checker for reviewing app launch risks.

**Version 0.1.0 — source triage plus guided review.** This tool identifies candidate issues and missing evidence. It does not certify security or legal compliance.

## What it does

- Flags six source patterns: possible embedded credentials, disabled SQL row-level security, remote Google Fonts, replay integrations, unconditional SQL policies, and privileged credentials referenced through public-prefixed configuration.
- Provides a project questionnaire covering markets, users, data, vendors, payments and deployment.
- Supplies 13 source-backed research records for project-specific review.
- Guides runtime checks for tenant isolation, cost controls, tracking, email suppression, subscriptions and accessibility.
- Keeps unknowns visible and gives contributors a documented review process.

## Quick start

Requirements: Python 3.9 or later. No third-party Python packages required.

From this repository's root:

```sh
python3 scripts/check.py /absolute/path/to/your-app
python3 scripts/check.py /absolute/path/to/your-app --profile /path/to/project-profile.json
python3 scripts/test_check.py
```

Copy `assets/project-profile.json` into your project's private working area and fill known values. Leave unknown values as `null`. The CLI records whether a profile was supplied; the skill uses the profile for guided analysis. The CLI does not evaluate legal applicability.

To write the JSON report, redirect stdout to a location outside the scanned project:

```sh
python3 scripts/check.py /path/to/app > /path/outside/app/launch-review.json
```

Exit codes:

| Code | Meaning |
|---|---|
| 0 | Scan completed; not a readiness approval |
| 1 | With `--fail-on-review`, at least one source candidate was found |
| 2 | Invalid root/profile; scan did not complete |

Unknown guided checks remain unknown regardless of exit code. The tool is not an all-clear CI gate.

## Using the skill

`SKILL.md` contains the workflow for a compatible coding agent. Follow your agent's skill installation process, retaining scripts, assets and references together. In ChatGPT, a separately installed personal copy can be invoked as Launch Readiness. Cloning this repository alone does not install a ChatGPT skill.

Example request:

> Use Launch Readiness to assess this app before launch. Investigate source candidates, test supported fixes in an isolated environment, and list remaining unknowns.

## Example finding

```json
{
  "rule_id": "DB-001",
  "status": "review",
  "severity": "high",
  "title": "SQL explicitly disables row-level security",
  "path": "schema.sql",
  "lines": [12],
  "confidence": "source-pattern-only"
}
```

A comment or fixture can match this detector. Verify context and actual authorization behavior before changing access policies.

## Coverage and limitations

The checker reads supported text files locally. It does not execute project code or contact external services. It reports paths and line numbers without matched source or credential values. Filenames may themselves be sensitive; review reports before sharing.

Symlinks are not read. Generated/vendor folders, unsupported extensions, files over 1 MiB, non-UTF-8 files and files beyond the 10,000-file limit are outside the scan. The report describes scope and applicable omissions.

No match means no detected pattern in the scanned scope. It does not mean the project is safe. Detectors use regular expressions rather than full language parsers. There are no live cloud adapters, automatic fixes, automatic legal decisions or scheduled monitoring in v0.1.0.

Legal research records are starting points, last researched 30 September 2026. Verify current primary sources, commencement dates, exceptions and project applicability before drawing conclusions. All records are marked as requiring current verification; none is represented as independently approved legal advice.

## Project layout

- `SKILL.md` — agent workflow
- `scripts/check.py` — read-only source checker
- `scripts/test_check.py` — 11 regression tests
- `assets/project-profile.json` — applicability questionnaire
- `references/rules.json` — source-backed review seeds
- `references/review-guide.md` — verification recipes and reporting
- `references/contributing.md` — contribution and release requirements
- `LICENSE` — MIT license for original project files

## Contributing

Start with a reproducible issue or small pull request. Include synthetic positive/negative fixtures for detector changes. For legal research, provide primary sources, exact sections, applicability, exceptions and effective dates. Do not submit customer data or live credentials. See `references/contributing.md`.

## Security

Do not publish credentials or exploitable private-project details in issues. A private security reporting channel has not yet been configured; request a private channel from the maintainer before disclosing sensitive details.

## Roadmap

- Behavior-based checks on isolated sample applications
- Better parsing and false-positive reduction
- Reviewed jurisdiction packs with versioned evidence
- Optional provider integrations

These are planned directions, not shipped capabilities.

## License

MIT. Third-party sources and linked documentation retain their own terms. This project contains original checks and summaries, not copied third-party rule packs.
