# Minimal web app example

A tiny synthetic fixture that exercises both sides of the readiness engine:

- `index.html` loads a remote Google Font, which triggers a **PRIV-001** source candidate (transfer/privacy review).
- `profile.json` declares an India nexus, which activates the India DPDP pack.
- `evidence.json` records a failed consent-UX runtime check using the `reference` locator alias.

Run from the repository root:

```sh
python3 scripts/check.py examples/minimal-web-app --profile examples/minimal-web-app/profile.json --evidence examples/minimal-web-app/evidence.json
```

Expected: one `REVIEW` source candidate (PRIV-001), `IN-DPDP-CONSENT-UX` as `FAIL`
(listed under `readiness_summary.dpdp_fail`), and the remaining DPDP duties as
`FUTURE_EFFECTIVE` or `UNKNOWN`. All data is synthetic.
