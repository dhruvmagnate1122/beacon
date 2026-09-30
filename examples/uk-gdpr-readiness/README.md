# UK GDPR + PECR example

Synthetic fixture for Beacon's UK jurisdiction pack.

- `profile.json` explicitly activates `uk-gdpr-pecr`.
- The profile models a non-UK service offering services to people in the UK.
- It also declares UK storage/access technologies and electronic direct marketing so the PECR subchecks are active.
- `evidence.json` records a failed runtime storage/access check.

Run:

```sh
python3 scripts/check.py examples/uk-gdpr-readiness \
  --profile examples/uk-gdpr-readiness/profile.json \
  --evidence examples/uk-gdpr-readiness/evidence.json
```

This is a readiness fixture, not UK GDPR/PECR certification.
