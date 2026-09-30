# Contributing to Beacon

Beacon is an early-warning readiness framework, not a legal-compliance certifier.

## Good contributions

- reduce a known false positive;
- improve runtime/config verification recipes;
- add a jurisdiction pack backed by current primary sources;
- add provider/cost-control checks;
- improve evidence provenance or freshness handling;
- add tests for commencement, applicability or evidence conflicts;
- improve documentation with reproducible examples.

## Legal-rule requirements

Any legal/compliance rule change must include:

- jurisdiction;
- exact source/provision;
- primary-source URL;
- applicability trigger;
- effective date / commencement state;
- material exceptions;
- evidence required;
- last research date;
- limitations.

Do not infer law from reels, blog posts, vendor marketing, or summaries when a primary source exists.

## Evidence rules

Static source patterns are candidates, not legal findings.

Evidence should record type, result, sanitized details, date/environment where relevant, reviewer/tool provenance, and an `artifact` or `reference` when reproducible.

Do not include credentials, customer data, or unnecessary personal data.

## Pull requests

1. Keep changes narrowly scoped.
2. Add or update regression tests.
3. Run:
   ```sh
   python3 scripts/test_check.py
   ```
4. Explain applicability and false-positive tradeoffs.
5. For legal changes, cite current primary sources and effective dates.

## Beginner-friendly contribution paths

- improve a `next_step` or runtime recipe;
- add a synthetic fixture;
- add a rule freshness test;
- improve a jurisdiction applicability questionnaire;
- add a provider cost-control research seed;
- add documentation for a common stack.

## We will reject

- claims that Beacon certifies legal compliance;
- unsourced legal rules;
- blanket assumptions that all startups are exempt or all cross-border transfers are banned;
- automatic penalty/fine totals;
- source regexes presented as proof of actual runtime behavior;
- real secrets or user/customer data in fixtures.
