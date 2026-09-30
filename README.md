# Beacon — Evidence-driven launch readiness for web apps

[![tests](https://github.com/dhruvmagnate1122/beacon/actions/workflows/tests.yml/badge.svg)](https://github.com/dhruvmagnate1122/beacon/actions/workflows/tests.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Catch privacy, regulatory, security, and operational gaps before launch — without pretending a scan is certification.**

Beacon is an open-source coding-agent skill plus a dependency-free Python readiness engine for web products. It combines conservative source signals, project facts, configuration review, runtime evidence, and primary-source-backed jurisdiction packs to show what is known, what failed, what needs review, what does not apply, and what is not yet effective.

> **Beacon is an early-warning system, not a compliance certificate.** A clean scan does not mean an app is secure, legally compliant, tax-correct, accessible, or operationally safe.

## Why Beacon

AI-assisted development can get a product deployed faster than teams can review the last mile: consent, data handling, incident readiness, subscriptions, accessibility, cloud-cost exposure, jurisdiction scope, and effective dates.

Beacon makes that review explicit and evidence-backed. Its core rule is simple:

**A source signal is not a legal finding, and missing evidence is not proof of a violation.**

## What it covers

Beacon combines four layers:

- **source triage** — conservative candidates for embedded credentials, disabled RLS, replay/tracking, remote fonts, public-prefixed privileged secrets, and unconditional SQL policies;
- **operational readiness** — tenant isolation, cost controls, unsubscribe/suppression, subscriptions/cancellation, accessibility, retention/deletion, and related runtime checks;
- **evidence + applicability** — project facts, config, questionnaire, runtime and legal evidence with provenance;
- **executable jurisdiction packs** — independent applicability, effective-date modeling and rule-level evidence requirements.

### Executable packs

| Pack | Focus | Important boundary |
| --- | --- | --- |
| **India DPDP** | DPDP Act 2023 + Rules 2025, 18 commencement-aware checks | Not a legal-compliance certificate |
| **EU/EEA GDPR + ePrivacy** | GDPR privacy/data protection + ePrivacy tracking/marketing | ePrivacy requires Member State review |
| **UK GDPR + PECR** | UK GDPR/DPA/DUAA + PECR storage/access and marketing | PECR scope is evaluated separately |
| **US federal digital** | COPPA, CAN-SPAM, DMCA §512(c), ADA web/mobile | Does not cover US state law |
| **India CERT-In** | 2022 cyber-security directions and incident/logging readiness | Incident classification remains fact-specific |
| **EU digital VAT / OSS** | Focused digital-services VAT, place of supply, OSS and evidence | Not a complete VAT/tax engine |

Pack files live in `references/` and contain their own research date, sources, limitations, applicability fields, required evidence, and runtime recipes.

## Example result shape

```text
BEACON READINESS: REVIEW_REQUIRED

ACTIVE PACKS
  india-dpdp
  eu-gdpr-eprivacy

INDIA DPDP
  IN-DPDP-NOTICE
    Status: FUTURE_EFFECTIVE
    Readiness: UNKNOWN
    Effective: 2027-05-13

SOURCE CANDIDATES
  SEC-001
    Status: REVIEW
    Meaning: candidate signal; verify context

UNKNOWNS
  COST-001
    Next: inspect plan caps, recharge, quotas and expensive endpoints
```

For a future-effective duty, `status` remains `FUTURE_EFFECTIVE` while `readiness_status` separately records the current implementation evidence.

## Quick start

Requirements: **Python 3.9+**. No third-party Python packages are required.

```sh
python3 scripts/check.py /absolute/path/to/your-app

python3 scripts/check.py /absolute/path/to/your-app \
  --profile /path/to/project-profile.json

python3 scripts/check.py /absolute/path/to/your-app \
  --profile /path/to/project-profile.json \
  --evidence /path/to/evidence.json

python3 scripts/test_check.py
```

Copy `assets/project-profile.json` into a private project workspace and fill only facts you actually know. Leave unknowns as `null`.

Select one or more packs explicitly:

```json
{
  "jurisdiction_packs": [
    "india-dpdp",
    "eu-gdpr-eprivacy",
    "uk-gdpr-pecr"
  ]
}
```

Available pack IDs:

```text
india-dpdp
eu-gdpr-eprivacy
uk-gdpr-pecr
us-federal-digital
india-certin
eu-digital-vat
```

## Evidence model

Evidence is an input contract, not proof of truth. Every evidence record requires:

- `type` — `source | config | questionnaire | runtime | legal`;
- `result` — `PASS | FAIL | REVIEW`;
- sanitized `details`;
- ISO-8601 `observed_at`;
- non-empty `environment`;
- producer/reviewer `{kind, name}`;
- either `artifact` or `reference` as a reproducible pointer.

Evidence `type` and `result` are accepted case-insensitively and normalized. Unknown rule IDs and evidence for inactive packs fail validation instead of being silently ignored.

## Status model

`PASS / FAIL / REVIEW / UNKNOWN / NOT_APPLICABLE / FUTURE_EFFECTIVE`

- **PASS** — the rule's declared evidence types contain passing evidence.
- **FAIL** — a required technical or behavioral verification failed; this is not automatically a legal violation.
- **REVIEW** — a candidate, conflict, or partial result needs contextual review.
- **UNKNOWN** — applicability or required evidence remains incomplete.
- **NOT_APPLICABLE** — the modeled applicability facts support non-applicability.
- **FUTURE_EFFECTIVE** — the modeled obligation is not yet effective; current readiness remains separate.

Beacon deliberately does **not** produce one global compliance score or pack-level certification.

## Trust boundaries

Beacon does not provide:

- legal, tax, security, or accessibility certification;
- automatic fines or penalty calculations;
- production changes or autonomous remediation;
- live cloud/provider access;
- autonomous browser/runtime execution;
- worldwide legal coverage;
- proof that a regex candidate is a real defect;
- a guarantee that a clean scan means a safe launch.

Legal/regulatory packs are research assets backed by primary sources and must be rechecked for amendments, guidance, effective dates, national implementation, and product-specific facts before legal conclusions.

## Repository map

- `SKILL.md` — coding-agent workflow
- `scripts/check.py` — source triage + multi-pack evidence engine
- `scripts/test_check.py` — regression suite
- `assets/project-profile.json` — project/applicability questionnaire
- `assets/evidence-example.json` — evidence contract example
- `references/india-dpdp.json` — India DPDP pack
- `references/eu-gdpr-eprivacy.json` — EU/EEA GDPR + ePrivacy pack
- `references/uk-gdpr-pecr.json` — UK GDPR + PECR pack
- `references/us-federal-digital.json` — selected US federal pack
- `references/india-certin.json` — India CERT-In pack
- `references/eu-digital-vat.json` — EU digital VAT/OSS pack
- `references/rules.json` — guided-review research seeds
- `references/review-guide.md` — verification recipes
- `docs/brand.md` — positioning and language guardrails
- `docs/launch-kit.md` — launch copy
- `CONTRIBUTING.md`, `ROADMAP.md`, `SECURITY.md`

## Contributing

Useful contributions include stronger runtime evidence recipes, false-positive reductions, jurisdiction freshness updates, new primary-source-backed packs, provider/cost adapters, synthetic fixtures, and pack-schema tests.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing legal/regulatory rules. Legal-rule changes must cite current primary sources, effective dates, applicability, exceptions, and limitations.

## Version

**v0.7.0** — six executable legal/regulatory packs across privacy, cyber-security, digital marketing/content/accessibility, and EU digital VAT.

MIT. Third-party sources and linked documentation retain their own terms.
