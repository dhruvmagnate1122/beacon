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
- **India DPDP pack** — 18 commencement-aware checks for the DPDP Act 2023 + Rules 2025;
- **EU/EEA GDPR + ePrivacy pack** — executable checks covering GDPR scope, principles, lawful basis, transparency, consent, special-category data, children, rights, automated decisions, processors, records, privacy by design, security, breach response, DPIA, DPO/representative duties, transfers, tracking/storage access and electronic marketing;
- **UK GDPR + PECR pack** — executable UK data-protection and privacy/electronic-communications checks updated for the Data (Use and Access) Act 2025, with separate applicability for UK GDPR, storage/access technologies and electronic marketing;
- **US federal digital-product pack** — selected federal checks for COPPA, CAN-SPAM, DMCA §512(c), and ADA web/mobile accessibility, with independent applicability for each regime;
- **India CERT-In pack** — executable readiness checks for the 28 April 2022 CERT-In cyber-security directions: time sync, six-hour incident reporting, point of contact, response readiness, 180-day logs, provider records and virtual-asset records where applicable;
- **EU digital VAT pack** — focused VAT/OSS readiness for cross-border digital services, including B2C TBE place of supply, the conditional EUR 10,000 threshold, customer-location evidence, B2B service treatment, OSS workflow and VAT-rate records.

## Example result shape

```text
BEACON READINESS: REVIEW_REQUIRED

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

Beacon keeps **candidate signals, legal applicability, future-effective duties, runtime evidence and unknowns separate**. For a future-effective duty, `status` remains `FUTURE_EFFECTIVE` while `readiness_status` records whether supplied evidence currently passes, fails, needs review, or remains unknown. Missing evidence is not converted into a legal violation.

## Quick start

Requirements: Python 3.9+. No third-party Python packages are required.

```sh
python3 scripts/check.py /absolute/path/to/your-app
python3 scripts/check.py /absolute/path/to/your-app --profile /path/to/project-profile.json
python3 scripts/check.py /absolute/path/to/your-app --profile /path/to/project-profile.json --evidence /path/to/evidence.json
python3 scripts/test_check.py
```

Copy `assets/project-profile.json` into a private project workspace and fill only facts you actually know. Leave unknowns as `null`. Select jurisdiction packs explicitly with `jurisdiction_packs` (for example `['india-dpdp']`, `['eu-gdpr-eprivacy']`, `['uk-gdpr-pecr']`, `['us-federal-digital']`, `['india-certin']`, `['eu-digital-vat']`, or any relevant combination). Applicability remains `UNKNOWN` when the facts are incomplete.

## Evidence trust model

`evidence.json` is an input contract, not proof of truth. Evidence may come from source inspection, configuration, questionnaires, runtime tests, or legal-source review. Evidence `type` and `result` vocabulary is accepted case-insensitively and normalized for evaluation.

For material readiness decisions, evidence should record:

- `type`;
- `result`;
- sanitized `details`;
- `observed_at` / review date;
- `environment` where relevant;
- producer/reviewer identity or tool;
- either `artifact` or `reference` — a required reproducible pointer to the supporting material.

The core validates this evidence structure, rejects evidence for unknown rule IDs or inactive jurisdiction packs, but does not cryptographically authenticate user-supplied evidence. Manual evidence should remain visibly manual. Conflicting or partial evidence should stay `REVIEW`; it should not be silently overwritten by a later assertion.

## Status model

`PASS / FAIL / REVIEW / UNKNOWN / NOT_APPLICABLE / FUTURE_EFFECTIVE`

- **PASS** — all evidence types declared by the rule are present and pass.
- **FAIL** — a required technical/behavioral verification failed; this is not automatically a legal violation.
- **REVIEW** — candidate, conflict, or partial evidence needs contextual review.
- **UNKNOWN** — applicability/current requirement exists but evidence is incomplete.
- **NOT_APPLICABLE** — facts support non-applicability and the rationale is retained.
- **FUTURE_EFFECTIVE** — the modeled obligation is not yet effective; any current implementation result is carried separately in `readiness_status`.

## Executable jurisdiction packs

### India DPDP

`references/india-dpdp.json` contains 18 evidence-driven checks for India.

The pack is researched as of **30 September 2026** against the DPDP Act 2023, final DPDP Rules 2025, the commencement notification, and MeitY's Rules collection/corrigendum. It models phased commencement so future-effective duties are not reported as present violations.

### EU/EEA GDPR + ePrivacy

`references/eu-gdpr-eprivacy.json` is Beacon's second executable pack. It models GDPR territorial/material scope and major launch-readiness obligations under the GDPR, plus ePrivacy terminal-equipment/tracking and electronic-marketing checks. ePrivacy is a Directive implemented through Member State law, so the pack explicitly requires market-specific legal review rather than pretending one national implementation is EU-wide.

The EU pack is researched as of **1 October 2026** against EUR-Lex, EDPB guidance and European Commission transfer materials.

### United Kingdom — UK GDPR + PECR

`references/uk-gdpr-pecr.json` is Beacon's third executable jurisdiction pack. It models UK GDPR/DPA 2018 launch-readiness after the Data (Use and Access) Act 2025, plus PECR storage/access and electronic-marketing checks. PECR subchecks use their own applicability signals rather than assuming UK GDPR territorial scope automatically decides PECR applicability.

The UK pack is researched as of **1 October 2026** against current UK legislation and ICO guidance. All DUAA data-protection provisions were in force by 19 June 2026; because ICO guidance is still being updated in some areas, current legislation and the newest ICO material should be checked on every release.

### United States — selected federal digital-product regimes

`references/us-federal-digital.json` is Beacon's fourth executable jurisdiction pack. It intentionally does **not** pretend the United States has one federal omnibus privacy law. Instead it models independent federal regimes that commonly affect digital products: COPPA for covered child-data processing, CAN-SPAM for commercial email, DMCA §512(c) safe-harbor operations for user-hosted content, and ADA web/mobile accessibility.

The amended COPPA Rule became effective **23 June 2025**, with most regulated entities required to comply by **22 April 2026**. The DOJ's 2026 interim final rule extended the Title II web/mobile compliance dates to **26 April 2027** for public entities of 50,000+ population and **26 April 2028** for smaller public entities/special districts. Title III business accessibility is kept separate because DOJ has not imposed the same specific federal web technical standard on private public accommodations.

### India — CERT-In cyber-security directions

`references/india-certin.json` is Beacon's fifth executable regulatory pack. It models the 28 April 2022 CERT-In directions and associated FAQ material for covered entities, including NTP/time synchronisation, reportable incidents within six hours, CERT-In point-of-contact readiness, 180-day ICT log retention in India, and the additional recordkeeping duties for specified data-centre/VPS/cloud/VPN and virtual-asset provider categories.

The six-hour reporting check follows the CERT-In FAQ approach: an initial report can contain information available at the time, with additional information supplied later within a reasonable time. Applicability and incident classification remain fact-specific; Beacon does not turn every security alert into a reportable incident.

### European Union — digital services VAT / OSS

`references/eu-digital-vat.json` promotes Beacon's existing EU-tax research seed into a focused executable pack. It does not attempt to be a complete VAT engine. The pack separates B2C telecommunications/broadcasting/electronic services, B2B cross-border services, the conditional EUR 10,000 threshold, customer-location evidence and OSS reporting.

The EUR 10,000 threshold is deliberately not treated as a generic startup or SaaS threshold: the Commission states that it applies only under specific establishment and supply conditions and is measured across the relevant current and preceding calendar-year supplies. The pack also avoids a universal “two location proofs” rule because EU implementing rules contain context- and turnover-dependent evidence presumptions.

The Commission published revised OSS explanatory notes/guidelines in July 2026 incorporating ViDA changes that begin entering into force from **1 January 2027**, so releases crossing that date require a fresh primary-source review.

**Always re-check current primary sources before making a legal conclusion.** Bundled legal records are research assets, not legal opinions.

## What Beacon does not do

- no legal certification or compliance badge;
- no automatic fine calculation;
- no production changes;
- no live cloud/provider access;
- no autonomous browser/runtime testing;
- no worldwide legal coverage; only selected executable jurisdiction packs plus research seeds;
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
- `references/india-dpdp.json` — India DPDP executable pack
- `references/eu-gdpr-eprivacy.json` — EU/EEA GDPR + ePrivacy executable pack
- `references/uk-gdpr-pecr.json` — UK GDPR + PECR executable pack
- `references/us-federal-digital.json` — selected US federal digital-product executable pack
- `references/india-certin.json` — India CERT-In cyber-security directions executable pack
- `references/eu-digital-vat.json` — EU digital-services VAT/OSS executable pack
- `references/rules.json` — broader guided-review research seeds
- `references/review-guide.md` — verification recipes
- `CONTRIBUTING.md` — contribution contract
- `ROADMAP.md` — project direction
- `SECURITY.md` — security reporting guidance

## Version

**v0.7.0** — six executable legal/regulatory packs across privacy, cyber-security, digital marketing/content/accessibility and EU digital VAT.

MIT. Third-party sources and linked documentation retain their own terms.
