#!/usr/bin/env python3
"""Read-only, dependency-free source triage. Never a compliance certification."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys

VERSION = '0.1.0'
SKIP = {'.git', 'node_modules', '.next', 'dist', 'build', '.venv', 'venv', '__pycache__', 'vendor', 'coverage'}
EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.html', '.css', '.sql', '.json', '.py', '.yml', '.yaml', '.toml'}
LIMIT = 1024 * 1024
MAX_FILES = 10000
# Evidence includes locations and rule explanations, never matched source or credential values.
PATTERNS = [
 ('SEC-001', 'high', 'Possible embedded private key or live credential', r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk_live_[A-Za-z0-9]{16,}|\bAKIA[A-Z0-9]{16}\b'),
 ('DB-001', 'high', 'SQL explicitly disables row-level security', r'\bDISABLE\s+ROW\s+LEVEL\s+SECURITY\b'),
 ('PRIV-001', 'medium', 'Remote Google Fonts dependency requires transfer/privacy review', r'https?://fonts\.(?:googleapis|gstatic)\.com'),
 ('PRIV-002', 'medium', 'Session-replay dependency or configuration needs runtime review', r'@sentry/replay|rrweb|sessionReplay|session_replay|replaysSessionSampleRate|hotjar|fullstory'),
 ('DB-002', 'medium', 'Unconditional SQL policy needs intended-public-access review', r'\b(?:USING|WITH\s+CHECK)\s*\(\s*true\s*\)'),
 ('SEC-002', 'high', 'Public-prefixed configuration references privileged credentials', r'\b(?:NEXT_PUBLIC_|VITE_|PUBLIC_)[A-Z0-9_]*(?:SERVICE_ROLE|SECRET_KEY|PRIVATE_KEY)[A-Z0-9_]*'),
]
MANUAL = [
 ('DB-003', 'Tenant isolation and live database grants', 'Test anonymous, owner, other tenant and privileged-server access in an isolated environment.'),
 ('COST-001', 'Provider spending and abuse limits', 'Inspect actual plan, recharge, supported caps, quotas, retries and expensive endpoints.'),
 ('MAIL-001', 'Marketing opt-out and suppression', 'Send only to a test inbox; verify unsubscribe and persistent suppression after re-import.'),
 ('SUB-001', 'Subscription consent and cancellation', 'Verify actual price, renewal notices, consent records, refund handling and cancellation with test payments.'),
 ('A11Y-001', 'Accessibility', 'Run a suitable accessibility engine and keyboard/screen-reader checks on actual user flows.'),
 ('LEGAL-001', 'Jurisdiction and effective-date applicability', 'Apply references/rules.json using the project profile; browse current primary sources before legal conclusions.'),
 ('PRIV-003', 'Consent, deletion and retention behavior', 'Check collection before consent where required, withdrawal propagation, processor deletion and retention exceptions.'),
]

def scan(root, profile=None):
 root = Path(root).resolve()
 if not root.is_dir():
  raise ValueError('Project root must be an existing directory.')
 findings, omissions = [], []
 scanned = 0
 for base, dirs, files in os.walk(root, followlinks=False):
  dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink())
  for name in sorted(files):
   path = Path(base)/name
   rel = path.relative_to(root).as_posix()
   if path.is_symlink():
    omissions.append({'path': rel, 'reason': 'symlink not read'})
    continue
   if path.suffix not in EXTENSIONS and not name.startswith('.env'):
    continue
   if scanned >= MAX_FILES:
    omissions.append({'path': rel, 'reason': 'file limit'})
    continue
   try:
    if path.stat().st_size > LIMIT:
     omissions.append({'path': rel, 'reason': 'over 1 MiB limit'}); continue
    raw = path.read_bytes()
    if b'\0' in raw: raise ValueError('binary')
    content = raw.decode('utf-8')
   except (OSError, UnicodeError, ValueError):
    omissions.append({'path': rel, 'reason': 'unreadable or non-UTF-8 text'}); continue
   scanned += 1
   for rule_id, severity, title, pattern in PATTERNS:
    matches = list(re.finditer(pattern, content, re.I))
    if matches:
     findings.append({'rule_id': rule_id, 'status': 'review', 'severity': severity,
      'title': title, 'path': rel, 'lines': sorted({content.count('\n', 0, m.start())+1 for m in matches})[:20],
      'confidence': 'source-pattern-only', 'meaning': 'Candidate signal; comments, fixtures and public-data exceptions can match.'})
 for rule_id, title, task in MANUAL:
  findings.append({'rule_id': rule_id, 'status': 'unknown', 'severity': 'unassessed', 'title': title, 'next_step': task})
 return {'version': VERSION, 'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
  'mode': 'read-only-source-triage', 'overall': 'incomplete-review-required',
  'scope': {'files_scanned': scanned, 'excluded_directories': sorted(SKIP), 'extensions': sorted(EXTENSIONS),
   'max_file_bytes': LIMIT, 'max_files': MAX_FILES, 'omissions': omissions},
  'profile_provided': profile is not None,
  'limitations': ['No live service, legal or runtime verification performed.',
   'No detected pattern means only no match within scanned files; it is not a pass.',
   'Source comments and strings can cause false positives; confirm context before fixing.',
   'No project code was executed and no source content or matched secret values are reported.'],
  'findings': findings}

def main():
 ap = argparse.ArgumentParser(description=__doc__)
 ap.add_argument('root')
 ap.add_argument('--profile', help='Project profile JSON; context only, never proof of compliance')
 ap.add_argument('--fail-on-review', action='store_true', help='Exit 1 when source candidates exist; unknowns still remain')
 args = ap.parse_args()
 try:
  profile = None
  if args.profile:
   profile = json.loads(Path(args.profile).read_text())
   if not isinstance(profile, dict): raise ValueError('Profile must be a JSON object.')
  result = scan(args.root, profile)
 except (OSError, ValueError) as exc:
  print(json.dumps({'error': type(exc).__name__, 'message': 'Invalid root or profile; no scan completed.'}), file=sys.stderr)
  return 2
 print(json.dumps(result, indent=2))
 return 1 if args.fail_on_review and any(f['status']=='review' for f in result['findings']) else 0

if __name__ == '__main__':
 sys.exit(main())
