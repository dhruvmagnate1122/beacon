#!/usr/bin/env python3
"""Read-only launch triage plus profile-driven India DPDP readiness. Never a compliance certification."""
import argparse, datetime as dt, json, os, re, sys
from pathlib import Path

VERSION='0.2.0'
SKIP={'.git','node_modules','.next','dist','build','.venv','venv','__pycache__','vendor','coverage'}
EXTENSIONS={'.js','.jsx','.ts','.tsx','.mjs','.cjs','.html','.css','.sql','.json','.py','.yml','.yaml','.toml'}
LIMIT=1024*1024; MAX_FILES=10000
PATTERNS=[
 ('SEC-001','high','Possible embedded private key or live credential',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk_live_[A-Za-z0-9]{16,}|\bAKIA[A-Z0-9]{16}\b'),
 ('DB-001','high','SQL explicitly disables row-level security',r'\bDISABLE\s+ROW\s+LEVEL\s+SECURITY\b'),
 ('PRIV-001','medium','Remote Google Fonts dependency requires transfer/privacy review',r'https?://fonts\.(?:googleapis|gstatic)\.com'),
 ('PRIV-002','medium','Session-replay dependency or configuration needs runtime review',r'@sentry/replay|rrweb|sessionReplay|session_replay|replaysSessionSampleRate|hotjar|fullstory'),
 ('DB-002','medium','Unconditional SQL policy needs intended-public-access review',r'\b(?:USING|WITH\s+CHECK)\s*\(\s*true\s*\)'),
 ('SEC-002','high','Public-prefixed configuration references privileged credentials',r'\b(?:NEXT_PUBLIC_|VITE_|PUBLIC_)[A-Z0-9_]*(?:SERVICE_ROLE|SECRET_KEY|PRIVATE_KEY)[A-Z0-9_]*')]
MANUAL=[('DB-003','Tenant isolation and live database grants','Test anonymous, owner, other tenant and privileged-server access in an isolated environment.'),('COST-001','Provider spending and abuse limits','Inspect actual plan, recharge, supported caps, quotas, retries and expensive endpoints.'),('MAIL-001','Marketing opt-out and suppression','Use a test inbox; verify unsubscribe and persistent suppression after re-import.'),('SUB-001','Subscription consent and cancellation','Verify price, renewal, consent records, refund handling and cancellation with test payments.'),('A11Y-001','Accessibility','Run a suitable accessibility engine and keyboard/screen-reader checks.'),('LEGAL-001','Jurisdiction and effective-date applicability','Apply current primary sources using the project profile; do not treat bundled research as legal advice.'),('PRIV-003','Consent, deletion and retention behavior','Check collection, withdrawal propagation, processor deletion and retention exceptions.')]

def dpdp(profile, base):
 pack=json.loads((base/'references/india-dpdp.json').read_text())
 if not profile: return []
 nexus=profile.get('offers_goods_or_services_to_people_in_india')
 est=profile.get('entity_establishments')
 india= nexus is True or (isinstance(est,list) and any(str(x).lower()=='india' for x in est)) or (isinstance(est,str) and 'india' in est.lower())
 if nexus is False and not india: return [{'rule_id':'IN-DPDP-SCOPE','status':'applicability-unknown','severity':'unassessed','title':'India DPDP scope requires factual review','next_step':'Confirm India establishment/offering/activity nexus and Act section 3 exclusions.'}]
 out=[]
 for c in pack['checks']:
  status=c['status_default']
  if not india: status='applicability-unknown'
  out.append({'rule_id':c['id'],'status':status,'severity':'unassessed','title':c['title'],'effective':c['effective'],'evidence_needed':c['evidence'],'next_step':c['verify']})
 return out

def scan(root,profile=None):
 root=Path(root).resolve()
 if not root.is_dir(): raise ValueError('Project root must be an existing directory.')
 findings=[]; omissions=[]; scanned=0
 for base,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink())
  for name in sorted(files):
   path=Path(base)/name; rel=path.relative_to(root).as_posix()
   if path.is_symlink(): omissions.append({'path':rel,'reason':'symlink not read'}); continue
   if path.suffix not in EXTENSIONS and not name.startswith('.env'): continue
   if scanned>=MAX_FILES: omissions.append({'path':rel,'reason':'file limit'}); continue
   try:
    if path.stat().st_size>LIMIT: omissions.append({'path':rel,'reason':'over 1 MiB limit'}); continue
    raw=path.read_bytes()
    if b'\0' in raw: raise ValueError('binary')
    content=raw.decode('utf-8')
   except (OSError,UnicodeError,ValueError): omissions.append({'path':rel,'reason':'unreadable or non-UTF-8 text'}); continue
   scanned+=1
   for rid,sev,title,pat in PATTERNS:
    ms=list(re.finditer(pat,content,re.I))
    if ms: findings.append({'rule_id':rid,'status':'review','severity':sev,'title':title,'path':rel,'lines':sorted({content.count('\n',0,m.start())+1 for m in ms})[:20],'confidence':'source-pattern-only','meaning':'Candidate signal; verify context before changing behavior.'})
 for rid,title,task in MANUAL: findings.append({'rule_id':rid,'status':'unknown','severity':'unassessed','title':title,'next_step':task})
 findings.extend(dpdp(profile,Path(__file__).parents[1]))
 return {'version':VERSION,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'mode':'read-only-source-triage-plus-guided-dpdp','overall':'incomplete-review-required','scope':{'files_scanned':scanned,'excluded_directories':sorted(SKIP),'extensions':sorted(EXTENSIONS),'max_file_bytes':LIMIT,'max_files':MAX_FILES,'omissions':omissions},'profile_provided':profile is not None,'limitations':['No live service, legal or runtime verification performed.','DPDP profile results are evidence prompts/statuses, not legal determinations.','Future-effective reflects the bundled commencement model and must be rechecked against current primary sources.','No detected source pattern means only no match within scanned files; it is not a pass.','No project code was executed and no source content or matched secret values are reported.'],'findings':findings}

def main():
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('root'); ap.add_argument('--profile'); ap.add_argument('--fail-on-review',action='store_true'); args=ap.parse_args()
 try:
  profile=None
  if args.profile:
   profile=json.loads(Path(args.profile).read_text())
   if not isinstance(profile,dict): raise ValueError('Profile must be a JSON object.')
  result=scan(args.root,profile)
 except (OSError,ValueError,json.JSONDecodeError):
  print(json.dumps({'error':'InvalidInput','message':'Invalid root or profile; no scan completed.'}),file=sys.stderr); return 2
 print(json.dumps(result,indent=2))
 return 1 if args.fail_on_review and any(f['status']=='review' for f in result['findings']) else 0
if __name__=='__main__': sys.exit(main())
