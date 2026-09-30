# Guided review

## Source and applicability

All bundled legal records are initial research seeds reviewed 2026-09-30, not a current legal opinion. Open their primary sources when needed; distinguish statutes, regulator guidance, court decisions, vendor contracts and engineering recommendations. Check current amendments and operative dates. Never infer all-country coverage from a list of source links. Do not derive rules or fines from social-media graphics.

Start with India/EU/UK/US if the project targets them, then add only relevant regions. India DPDP is phased; verify the separate Act commencement notification and rule corrigenda. Startup exemptions require applicable evidence. A cookie banner alone is insufficient. Consent is not the only possible lawful ground. Children, tax, health and AI rules need separate classification. Using AI to write code does not alone make the product an AI system.

## Verification recipes

- Database: seed two tenants; test anonymous, each owner and cross-tenant select/insert/update/delete in an isolated database. Check grants, views, storage and server authorization. Confirm intentional public records still work. Never use actual customer data.
- Cost: inspect actual plan and recharge settings; distinguish alert and cap; verify service coverage, reporting lag and availability impact. Test bounded retries, rate/concurrency limits and expensive endpoints locally.
- Tracking: capture network requests before any choice, after acceptance, rejection and withdrawal. Confirm masking and processor behavior. Scope each assertion to the actual flow/version.
- Email: use a test inbox/provider sandbox. Verify unsubscribe works, suppression survives re-import, sender details are correct and channel/jurisdiction rules were reviewed.
- Subscriptions: use test mode. Verify price/period, consent record, cancellation and webhook idempotency. Tax obligations and legal refund conclusions need separate evidence.
- Accessibility: use an established engine plus manual keyboard/focus/screen-reader testing; document tested pages and remaining gaps. Scanner success is not legal certification.
- Privacy lifecycle: trace collection to vendors, retention, account deletion and backups; preserve legal holds and keep consent evidence minimal. Do not assume deletion from one table deletes every copy.

## Output

State project/version, environment, profile unknowns, date, scan coverage and omitted files. Separate source candidates from verified issues. For each finding record ID, source/date, applicability rationale, sanitized evidence, confidence, fix, test/result and owner. End with release blockers, accepted risks and unknowns. Never sum hypothetical penalties.

## v0.1 boundaries

Automated: six source-pattern signals in check.py. Guided only: live database authorization, provider caps, consent, email, payments, accessibility, legal applicability. No auto-fix engine, cloud adapter, scheduled monitoring, SARIF exporter or worldwide legal certification is included. Rule records do not execute or calculate applicability. The profile is context for the assistant and is not evaluated by the CLI.
