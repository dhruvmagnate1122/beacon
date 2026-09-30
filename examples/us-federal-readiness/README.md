# US federal digital-product example

Synthetic fixture for Beacon's US federal pack.

- activates `us-federal-digital`;
- models a child-directed product collecting personal information;
- sends commercial email;
- hosts user-uploaded content and seeks DMCA §512(c) safe-harbor treatment;
- models a Title III public accommodation;
- records a failed COPPA runtime consent check.

Run:

```sh
python3 scripts/check.py examples/us-federal-readiness \
  --profile examples/us-federal-readiness/profile.json \
  --evidence examples/us-federal-readiness/evidence.json
```

This fixture is not legal certification and does not model state law.
