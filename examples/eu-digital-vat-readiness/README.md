# EU digital VAT example

Synthetic fixture for Beacon's EU digital-services VAT/OSS pack.

- activates `eu-digital-vat`;
- models B2C electronically supplied services to consumers in multiple EU Member States;
- models a supplier established in one Member State and using OSS;
- records a failed runtime test for customer-location evidence.

Run:

```sh
python3 scripts/check.py examples/eu-digital-vat-readiness \
  --profile examples/eu-digital-vat-readiness/profile.json \
  --evidence examples/eu-digital-vat-readiness/evidence.json
```

This fixture is not tax advice or a tax-authority determination.
