# Beacon — Launch Readiness

**Catch launch risks before your users, regulators, vendors, or cloud bill do.**

Beacon is an open-source coding-agent skill plus lightweight Python readiness engine for web products. It combines conservative source signals, project facts, configuration review, runtime evidence, and current legal-source verification to surface what still needs attention before launch.

> **Beacon is an early-warning system, not a compliance certificate.** A clean scan does not mean an app is secure, legally compliant, tax-correct, accessible, or operationally safe.

## What Beacon looks for

Beacon currently combines:

- **source candidates** — embedded credentials, disabled RLS, session replay, public-prefixed privileged secrets, remote Google Fonts and unconditional SQL policies;
- **project facts** — markets, users, personal data, consent, vendors, children, payments, subscriptions, AI features, retention and hosting;
- **runtime/config review** — tenant isolation, cost controls, tracking, unsubscribe/suppression, subscriptions, accessibility and deletion behavior;
- **legal-source verification** — jurisdiction/effective-date review using primary sources;
- **India DPDP pack** — 18 commencement-aware readiness checks covering scope, notice, consent, consent UX, consent evidence, security, breach response, rights, children, cross-border processing, SDF duties and exemptions.

## Example result shape

```text
CANARY READINESS: REVIEW_REQUIRED

SOURCE CANDIDATES
  [HIGH] SEC-001
    Possible embedded private credential
    Status: REVIEW
    Next: inspect context and rotate if live

INDIA DPDP
  IN-DPDP-NOTICE
    Status: FUTURE_EFFECTIVE
    Effective: 2027-05-13
    Next: prepare notice evidence before commencement

UNKNOWNS
  COST-001
    Provider spending and abuse limits
    Next: inspect plan caps, recharge, quotas and expensive endpoints
```

Beacon keeps **candidate signals, legal applicability, future-effective duties, runtime evidence and unknowns separate**. It does not turn missing evidence directly into a legal violation.

## Quick start

Requirements: Python 3.9+. No third-party Python packages are required.

```sh
python3 scripts/check.py /absolute/path/to/your-app
python3 scripts/check.py /absolute/path/to/your-app --profile /path/to/project-profile.json
python3 scripts/check.py /absolute/path/to/your-app --profile /path/to/project-profile.json --evidence /path/to/evidence.json
python3 scripts/test_check.py
```

Copy `assets/project-profile.json` into a private project workspace and fill only facts you actually know. Leave unknowns as `null`.

## Evidence trust model

`evidence.json` is an input contract, not proof of truth. Evidence may come from source inspection, configuration, questionnaires, runtime tests, or legal-source review.

For material readiness decisions, evidence should record:

- `type`;
- `result`;
- sanitized `details`;
- `observed_at` / review date;
- `environment` where relevant;
- producer/reviewer identity or tool;
- either `artifact` or `reference` — a required reproducible pointer to the supporting material.

The core validates this evidence structure but does not cryptographically authenticate user-supplied evidence. Manual evidence should remain visibly manual. Conflicting or partial evidence should stay `REVIEW`; it should not be silently overwritten by a later assertion.

## Status model

`PASS / FAIL / REVIEW / UNKNOWN / NOT_APPLICABLE / FUTURE_EFFECTIVE`

- **PASS** — all evidence types declared by the rule are present and pass.
- **FAIL** — a required technical/behavioral verification failed; this is not automatically a legal violation.
- **REVIEW** — candidate, conflict, or partial evidence needs contextual review.
- **UNKNOWN** — applicability/current requirement exists but evidence is incomplete.
- **NOT_APPLICABLE** — facts support non-applicability and the rationale is retained.
- **FUTURE_EFFECTIVE** — the modeled obligation is not yet effective.

## India DPDP pack

`references/india-dpdp.json` contains 18 evidence-driven checks for India.

The pack is researched as of **30 September 2026** against the DPDP Act 2023, final DPDP Rules 2025, the commencement notification, and MeitY's Rules collection/corrigendum. It models phased commencement so future-effective duties are not reported as present violations.

**Always re-check current primary sources before making a legal conclusion.** Bundled legal records are research assets, not legal opinions.

## What Beacon does not do

- no legal certification or compliance badge;
- no automatic fine calculation;
- no production changes;
- no live cloud/provider access;
- no autonomous browser/runtime testing;
- no worldwide legal coverage;
- no guarantee that a source regex match is a real defect;
- no guarantee that a clean scan means a safe launch.

## Why this exists

AI-assisted development makes it easy to get from idea to deployment faster than teams can perform the last-mile checks around privacy, consent, subscriptions, cost exposure, data isolation and jurisdiction-specific obligations.

Beacon tries to make that last mile explicit and evidence-backed instead of relying on a generic “launch checklist.”

## Contributing

Useful contributions include:

- new jurisdiction packs backed by current primary sources;
- stronger runtime evidence recipes;
- false-positive reductions;
- provider/cost-control adapters;
- subscription and marketing-flow checks;
- rule freshness/versioning improvements.

Start with [CONTRIBUTING.md](CONTRIBUTING.md), the [roadmap](ROADMAP.md), or a `good first issue`.

Legal-rule changes must cite current primary sources, effective dates, applicability and exceptions. Never publish live credentials, customer data, or private-project exploit details.

## Project layout

- `SKILL.md` — Beacon coding-agent workflow
- `scripts/check.py` — source triage + profile/evidence-driven readiness engine
- `scripts/test_check.py` — regression tests
- `assets/project-profile.json` — project/applicability questionnaire
- `assets/evidence-example.json` — evidence format
- `references/india-dpdp.json` — India DPDP validation pack
- `references/rules.json` — broader research seeds
- `references/review-guide.md` — verification recipes
- `CONTRIBUTING.md` — contribution contract
- `ROADMAP.md` — project direction
- `SECURITY.md` — security reporting guidance

## Version

**v0.2.0** — evidence-driven launch readiness with India DPDP support.

MIT. Third-party sources and linked documentation retain their own terms.
