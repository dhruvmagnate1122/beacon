# India CERT-In example

Synthetic fixture for Beacon's CERT-In cyber-security directions pack.

- activates `india-certin`;
- models an entity subject to the general CERT-In directions and incident-reporting workflow;
- models a cloud-service provider category for subscriber-record duties;
- records a failed runtime test for 180-day logging readiness.

Run:

```sh
python3 scripts/check.py examples/india-certin-readiness \
  --profile examples/india-certin-readiness/profile.json \
  --evidence examples/india-certin-readiness/evidence.json
```

This fixture is not CERT-In certification or a legal determination.
