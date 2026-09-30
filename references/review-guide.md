# Guided review

## Source and applicability

Bundled legal records and executable packs are research assets, not legal opinions. India DPDP was reviewed 2026-09-30; the EU/EEA GDPR + ePrivacy, UK GDPR + PECR, US federal digital-product, and India CERT-In packs were reviewed 2026-10-01. Open current primary sources; distinguish statutes, rules, notifications, regulator guidance, decisions, vendor contracts and engineering recommendations.

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

## EU/EEA GDPR + ePrivacy verification

- Scope: establish whether GDPR Article 3 applies through EU/EEA establishment context or, for a non-EU/EEA controller/processor, offering goods/services to or monitoring the behaviour of people in the Union. Do not infer targeting solely from technical accessibility.
- Principles/lawful basis: map each material processing purpose to an Article 6 basis and test actual minimisation, purpose and retention behavior rather than relying only on policy text.
- Transparency/consent: inspect the actual collection flow and privacy information; when consent is relied on, test affirmative choice and withdrawal against GDPR Articles 4(11) and 7 and current EDPB guidance.
- Rights: exercise representative access, rectification, erasure, restriction, portability and objection workflows with safe synthetic data; record applicable exceptions rather than assuming every right always applies.
- Children: determine the relevant Member State threshold under Article 8 where consent is the basis for an information-society service offered directly to a child.
- Roles/processors: determine controller/processor/joint-controller roles per processing activity and compare actual subprocessors/data flows with Article 28 arrangements.
- Design/security/breach: test defaults, access boundaries and incident workflows; apply Articles 25, 32-34 based on actual risk and context.
- DPIA/DPO/representative: determine applicability from Articles 27 and 35-39 and relevant regulator lists/guidance rather than job titles or company size alone.
- Transfers: inventory actual third-country access/processing and the relied-on Chapter V mechanism; re-check adequacy decisions, SCC use and other safeguards.
- ePrivacy: inspect terminal-equipment storage/access and electronic marketing separately from the GDPR. Because Directive 2002/58/EC is implemented by Member State law, verify the national law/guidance for each relevant market or establishment before drawing conclusions.

## UK GDPR + PECR verification

- Scope: determine UK GDPR applicability from UK establishment, targeted offering/monitoring or public-international-law facts; do not treat technical accessibility alone as targeting.
- DUAA: verify current law and ICO guidance after the Data (Use and Access) Act 2025. All data-protection provisions were in force by 19 June 2026, but some ICO guidance remains in active update cycles.
- Lawful basis/transparency: map each material purpose to the current UK lawful-basis framework and confirm privacy information matches real processing.
- Children/design: where online services are likely to be accessed by children, include the Children's Code and DUAA higher-protection matters in design/default review.
- Automated decisions: apply current Articles 22A-22D rather than pre-DUAA Article 22 shorthand; distinguish special-category restrictions from safeguards applicable to significant solely automated decisions.
- Rights/complaints: exercise rights requests and the organisation's complaint route; verify the current DUAA acknowledgement/response process.
- Transfers: apply current UK restricted-transfer analysis, adequacy regulations and appropriate safeguards; do not copy the EU transfer analysis blindly.
- PECR storage/access: treat regulation 6 technologies separately from UK GDPR scope; test cookies, pixels, local storage, fingerprinting/scripts and any relied-on DUAA exceptions.
- PECR marketing: test consent/soft-opt-in, identity and suppression for the actual electronic-marketing channel; include the charitable soft opt-in only where its conditions are actually met.

## US federal digital-product verification

- COPPA: classify the audience and actual-knowledge facts before testing child-data controls. The amended Rule is current; verify direct/online notices, verifiable parental consent where required, separate third-party/advertising consent where applicable, parental review/deletion controls, security and retention/deletion.
- CAN-SPAM: classify the message's primary purpose, then test sender/header/subject accuracy, postal-address disclosure, opt-out visibility/function and suppression. Do not treat SMS as CAN-SPAM email.
- DMCA §512(c): first confirm the service hosts material at user direction and is seeking that safe harbor. Then verify designated-agent registration/publication, notice/takedown/counter-notice operations and a reasonably implemented repeat-infringer policy. Do not treat safe-harbor process as a copyright merits decision.
- ADA Title III: determine whether the business is a covered public accommodation, then test accessibility with automated and manual techniques. WCAG is useful technical guidance; Beacon does not convert a WCAG failure directly into a Title III legal finding.
- ADA Title II: use the DOJ web/mobile rule only for covered state/local public entities. Track the 26 April 2027 or 26 April 2028 compliance date based on entity size/type and test against WCAG 2.1 Level AA subject to the rule's scope and exceptions.

## India CERT-In verification

- Scope: determine whether the general directions apply to the entity, and separately whether incident-reporting, provider-record or virtual-asset-record provisions are relevant. Do not infer provider classification from product branding alone.
- Time sync: inspect actual system time sources and drift; the Directions require NIC/NPL or traceable sources, with an alternative accurate standard source allowed for multi-geography infrastructure so long as it does not deviate from NIC/NPL.
- Incident reporting: tabletop an Annexure-I incident and verify an initial CERT-In report can be made within six hours of notice using information then available; later details can be supplemented.
- Point of contact/assistance: verify the nominated CERT-In contact is current and incident responders can handle a time-bound information or assistance direction.
- Logs: verify representative ICT logs are enabled, securely retained for a rolling 180 days, stored within India, and retrievable for incident reporting or a CERT-In direction.
- Provider records: apply only to listed data-centre/VPS/cloud/VPN categories; verify the required customer/subscriber fields and five-year post-cancellation retention workflow.
- Virtual assets: apply only to covered virtual-asset providers/exchanges/custodian wallets; verify five-year KYC/transaction record retention and transaction reconstruction fields.

## Other verification recipes

- Database: seed two tenants; test anonymous, owner, cross-tenant and privileged access in isolation.
- Cost: inspect actual plan/recharge/caps/quotas/retries and expensive endpoints.
- Tracking: capture network requests before choice and after acceptance, rejection and withdrawal.
- Email: use test inbox/provider sandbox; verify unsubscribe and persistent suppression.
- Subscriptions: use test mode; verify price/period, consent record, cancellation and webhook idempotency.
- Accessibility: established automated engine plus manual keyboard/focus/screen-reader checks.

## Output

State project/version, environment, profile unknowns, evidence date, scan coverage and omissions. Separate source candidates, verified behavior, legal applicability and future-effective readiness. For each item record ID, source/date, applicability rationale, sanitized evidence, confidence, fix/next action, test result and owner. Never sum hypothetical penalties.

## v0.6.0 boundaries

Automated source triage remains six regex signals. Beacon has five executable legal/regulatory packs: `india-dpdp`, `eu-gdpr-eprivacy`, `uk-gdpr-pecr`, `us-federal-digital`, and `india-certin`. Packs add profile-driven applicability, statuses and evidence prompts; the CLI does not parse privacy notices, make legal determinations or autonomously execute runtime tests. Tax and non-promoted US state/sector entries remain guided-review research seeds. No auto-fix engine, cloud adapter, scheduled monitoring, SARIF exporter or worldwide certification is included.


## Evidence and status engine

Each executable-pack check declares required evidence types from: `source`, `config`, `questionnaire`, `runtime`, and `legal`. Evidence keys must match a known rule ID in an executable pack; unknown IDs are rejected rather than silently ignored.

- `PASS`: all declared evidence types are present with passing evidence after the requirement is effective.
- `FAIL`: a required technical or behavioral verification failed. Do not translate this automatically into a statutory violation.
- `REVIEW`: a candidate, conflict, or partial result needs contextual review.
- `UNKNOWN`: the requirement is current/applicable but evidence is incomplete, or India nexus cannot yet be established.
- `NOT_APPLICABLE`: factual applicability review supports non-applicability and the rationale is retained.
- `FUTURE_EFFECTIVE`: the modeled obligation is not yet effective. When evidence exists, `readiness_status` separately records `PASS`, `FAIL`, `REVIEW`, or `UNKNOWN` without converting a future duty into a present legal failure.

Every evidence record must include `type`, `result`, concise sanitized `details`, `observed_at`, `environment`, producer/reviewer provenance, and either an `artifact` or `reference` reproducible pointer. `type` and `result` vocabulary is accepted case-insensitively and normalized before derivation. Accepted evidence results are `PASS`, `FAIL`, and `REVIEW`; `UNKNOWN`, `NOT_APPLICABLE`, and `FUTURE_EFFECTIVE` are derived readiness statuses rather than evidence assertions. Never put credentials, customer data or unnecessary personal data into evidence files.

For consent UX, use a clean browser/test account and verify the default state, required-only/reject path, pre-consent network behavior, affirmative acceptance, and withdrawal. Treat UI prominence or dark-pattern concerns as review evidence unless a specific legal conclusion is supported by current primary authority.


## India scope modeling

For Act section 3, Beacon requires explicit facts for the applicable route instead of inferring scope from founder location or visitor IP. It distinguishes: processing in India of personal data collected digitally or later digitised; qualifying processing outside India connected to offering goods or services to Data Principals in India; and section 3(c) exclusions declared to cover all relevant processing. The profile uses those explicit route facts only; the older unused `processing_connected_with_activity_outside_india` field has been removed. Partial facts remain `UNKNOWN`. `NOT_APPLICABLE` requires both routes to be affirmatively ruled out or an all-relevant-processing exclusion to be established and should still be supported by legal review before relying on it operationally.

## SDF modeling

`IN-DPDP-SDF` is conditional on current Significant Data Fiduciary designation evidence. Review Act section 10 and final Rule 13, including annual DPIA/audit, reporting significant observations to the Board, due diligence for technical measures including algorithmic software, DPO/auditor duties, and any personal-data/traffic-data transfer restriction specified under Rule 13(4).


## Multi-jurisdiction operation

Use `jurisdiction_packs` to select one or more executable packs. Findings retain `pack_id` and `jurisdiction`, and `readiness_summary.packs` rolls each pack up separately. Evidence for an unknown rule ID or a rule in an inactive pack is rejected so evidence cannot be silently attached to the wrong legal regime.

A pack-level `PASS` is intentionally not produced. Individual rule `PASS` means only that the rule's declared evidence types contain passing assertions under the current applicability model. Cross-jurisdiction conflicts, national derogations and sector-specific overlays must remain explicit legal review rather than being collapsed into one global compliance score.


## Rule-level applicability

A jurisdiction pack may contain rules whose legal scope is not identical to the pack's default data-protection scope. A check can therefore declare its own `applicability_model`. The UK pack uses this for PECR storage/access and electronic-marketing rules so a UK GDPR `NOT_APPLICABLE` result does not automatically suppress a PECR check, and vice versa.
