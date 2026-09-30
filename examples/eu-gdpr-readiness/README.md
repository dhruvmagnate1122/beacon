# EU/EEA GDPR + ePrivacy example

A synthetic fixture for Beacon's second executable jurisdiction pack.

- `profile.json` explicitly activates `eu-gdpr-eprivacy`.
- The profile models a non-EU product offering services to people in the EU/EEA.
- `evidence.json` records a failed runtime consent check for `EU-GDPR-CONSENT`.
- `index.html` includes a simple optional-analytics toggle and a remote Google Fonts link so the source triage still produces an independent privacy-review candidate.

Run from the repository root:

```sh
python3 scripts/check.py examples/eu-gdpr-readiness \
  --profile examples/eu-gdpr-readiness/profile.json \
  --evidence examples/eu-gdpr-readiness/evidence.json
```

The EU pack is a readiness model, not a GDPR/ePrivacy certification. ePrivacy requirements must be checked against the relevant Member State implementation.
