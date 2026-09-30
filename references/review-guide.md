# Guided review

## Source and applicability

Bundled legal records are research seeds reviewed 2026-09-30, not legal opinions. Open current primary sources; distinguish statutes, rules, notifications, regulator guidance, decisions, vendor contracts and engineering recommendations.

For India, use `india-dpdp.json`. The 13 November 2025 Act commencement notification phases substantive provisions; the final DPDP Rules likewise phase commencement, and MeitY lists a December 2025 corrigendum. Therefore a missing future-effective control is a readiness gap, not automatically a present statutory violation. Recheck notifications on every release.

## India DPDP verification

- Scope: document establishment, target market, offering/activity nexus, digital-personal-data categories and exclusions.
- Notice: inspect the actual standalone notice and collection screens; map itemised data to specified purposes and rights/withdrawal access.
- Consent/basis: trace each processing purpose to consent or the exact relied-on specified legitimate use; test withdrawal where consent applies.
- Security: inspect access controls, credential handling, encryption/obfuscation/tokenisation where appropriate, logs/monitoring, backups and processor safeguards; validate behavior technically.
- Breach: tabletop a synthetic incident; verify detection, evidence preservation, affected-person communication and Board-notification workflow without causing a real incident.
- Retention/erasure: trace active stores, processors and backups; document legal/business retention needs and verify the deletion workflow.
- Children: establish audience/age facts and test the verifiable parent/guardian mechanism where applicable; check tracking/advertising restrictions and exemptions.
- Rights/grievance: exercise test access, correction, erasure, nomination and grievance paths with safe synthetic accounts; record authentication and escalation.
- SDF: require current designation evidence before applying SDF-specific duties; if designated, inspect DPO, independent audit and required assessments.
- Cross-border: inventory destinations/vendors and check current Central Government restrictions; do not assume blanket localisation.
- Consent Manager: distinguish a registered Consent Manager under the Act/Rules from ordinary consent-management UI.

## Other verification recipes

- Database: seed two tenants; test anonymous, owner, cross-tenant and privileged access in isolation.
- Cost: inspect actual plan/recharge/caps/quotas/retries and expensive endpoints.
- Tracking: capture network requests before choice and after acceptance, rejection and withdrawal.
- Email: use test inbox/provider sandbox; verify unsubscribe and persistent suppression.
- Subscriptions: use test mode; verify price/period, consent record, cancellation and webhook idempotency.
- Accessibility: established automated engine plus manual keyboard/focus/screen-reader checks.

## Output

State project/version, environment, profile unknowns, evidence date, scan coverage and omissions. Separate source candidates, verified behavior, legal applicability and future-effective readiness. For each item record ID, source/date, applicability rationale, sanitized evidence, confidence, fix/next action, test result and owner. Never sum hypothetical penalties.

## v0.2 boundaries

Automated source triage remains six regex signals. The India pack adds profile-driven statuses/evidence prompts; it does not parse privacy notices, make legal determinations or execute runtime tests. No auto-fix engine, cloud adapter, scheduled monitoring, SARIF exporter or worldwide certification is included.
