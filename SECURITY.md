# Security policy

Launch Readiness is a review tool and may itself have security defects.

If you find a vulnerability that could expose secrets, execute unintended code, corrupt evidence, or otherwise create security risk, please avoid publishing exploit details in a public issue until the maintainer has had a reasonable opportunity to assess it. Until a private security reporting channel exists, ask the maintainer for a private channel first — do not invent an address or advertise a channel that does not exist.

For ordinary false positives, false negatives, missing checks, or rule-design concerns, use a normal GitHub issue.

Launch Readiness does not execute target project code during its dependency-free static triage and reports paths and line numbers without matched source or credential values. Contributions should preserve that boundary unless a future adapter explicitly documents and isolates runtime execution.
