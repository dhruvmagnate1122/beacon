# Contributing to Launch Readiness

Propose one independently reviewable change at a time. Include the problem, scope, reproducible fixture, expected result and limitations. Use synthetic data. Never commit customer records or real keys.

For a rule, include a stable ID, jurisdiction, actor/trigger, exceptions, effective-date status, exact primary source/section, verification date, reviewer status, evidence required and automation level. Explain changes from prior versions. Do not label a proposal reviewer-approved.

For detectors, add positive, negative, unknown and relevant exception fixtures. Treat parsers and regex signals according to what they actually prove. Keep network-free default execution and redacted output. Test empty projects, unreadable/oversized files and symlinks. Avoid executing project code. Run scripts/test_check.py and the skill validator before release.

For fixes, add before/after behavioral tests and rollback guidance. Legal interpretations require qualified review before being marketed as authoritative. Maintainers merge reviewed contributions; inclusion is not a certification.

Use semantic versioning: behavior/schema breaking changes require a major version; new compatible checks a minor version; corrections a patch. Existing reports retain their rule and tool versions. MIT applies to original project files. Check third-party licenses individually. Do not reuse commercially restricted rules as if permissively licensed.

Security reports: avoid public exploit details or credentials. Until a private security reporting channel is configured, ask the maintainer for a private channel; do not invent an address or advertise a channel that does not exist.

Release gate: tests pass; source scope and limitations accurate; no unsupported compliance claims; no customer artifacts bundled; contribution and license terms present. Public GitHub publication is a separate operation from personal skill installation.
