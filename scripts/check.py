#!/usr/bin/env python3
"""Read-only launch triage plus evidence-driven India DPDP readiness. Never a compliance certification."""
import argparse, datetime as dt, json, os, re, sys
from pathlib import Path

VERSION='0.2.0'
STATUSES={'PASS','FAIL','REVIEW','UNKNOWN','NOT_APPLICABLE','FUTURE_EFFECTIVE'}
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
MANUAL=[
 ('DB-003','Tenant isolation and live database grants','Test anonymous, owner, other tenant and privileged-server access in an isolated environment.'),
 ('COST-001','Provider spending and abuse limits','Inspect actual plan, recharge, supported caps, quotas, retries and expensive endpoints.'),
 ('MAIL-001','Marketing opt-out and suppression','Use a test inbox; verify unsubscribe and persistent suppression after re-import.'),
 ('SUB-001','Subscription consent and cancellation','Verify price, renewal, consent records, refund handling and cancellation with test payments.'),
 ('A11Y-001','Accessibility','Run a suitable accessibility engine and keyboard/screen-reader checks.'),
 ('LEGAL-001','Jurisdiction and effective-date applicability','Apply current primary sources using the project profile; do not treat bundled research as legal advice.'),
 ('PRIV-003','Consent, deletion and retention behavior','Check collection, withdrawal propagation, processor deletion and retention exceptions.')]

EVIDENCE_RESULTS={'PASS','FAIL','REVIEW','NOT_APPLICABLE','SUGGESTION','CLAIM_NEEDS_EVIDENCE'}
PRODUCER_KINDS={'tool','external','manual'}

def validate_evidence(evidence):
 """Fail loudly on malformed evidence so a typo'd file can never silently
 become UNKNOWN. Accepts 'artifact' or 'reference' as the reproducible
 locator, matching the documented evidence contract."""
 if not isinstance(evidence,dict):
  raise ValueError('Evidence must be an object mapping rule IDs to record arrays.')
 for rid,items in evidence.items():
  if not isinstance(items,list):
   raise ValueError('Evidence records for '+str(rid)+' must be an array.')
  for item in items:
   if not isinstance(item,dict):
    raise ValueError('Evidence record must be an object.')
   for k in ('type','result','details','observed_at','environment','producer'):
    if k not in item:
     raise ValueError('Evidence record missing '+k)
   artifact=item.get('artifact'); reference=item.get('reference')
   if not ((isinstance(artifact,str) and artifact.strip()) or (isinstance(reference,str) and reference.strip())):
    raise ValueError('Evidence record requires artifact or reference')
   if str(item['result']).upper() not in EVIDENCE_RESULTS:
    raise ValueError('Invalid evidence result')
   prod=item['producer']
   if not isinstance(prod,dict) or prod.get('kind') not in PRODUCER_KINDS or not prod.get('name'):
    raise ValueError('Invalid producer')
 return evidence

def readiness_summary(findings,today=None):
 """Mechanical rollup of findings: counts by status plus the DPDP rule IDs
 that failed, need review, are future-effective, or are still unknown.
 Pure arithmetic over existing statuses; not a legal determination."""
 today=today or dt.datetime.now(dt.timezone.utc).date()
 counts={}; dpdp_fail=[]; dpdp_review=[]; dpdp_future=[]; dpdp_unknown=0
 for f in findings:
  st=f.get('status'); counts[st]=counts.get(st,0)+1
  rid=f.get('rule_id','')
  if not rid.startswith('IN-DPDP'): continue
  if st=='FAIL': dpdp_fail.append(rid)
  elif st=='REVIEW': dpdp_review.append(rid)
  elif st=='FUTURE_EFFECTIVE': dpdp_future.append(rid)
  elif st=='UNKNOWN': dpdp_unknown+=1
 return {
  'counts_by_status':counts,
  'dpdp_fail':dpdp_fail,
  'dpdp_review':dpdp_review,
  'dpdp_future_effective':dpdp_future,
  'dpdp_unknown_count':dpdp_unknown,
  'note':'Mechanical rollup only; not a compliance determination. Recheck current primary sources before legal conclusions.'}

def _date(v):
 if v=='current': return None
 return dt.date.fromisoformat(v)

def _india_nexus(profile):
 if not profile: return None
 nexus=profile.get('offers_goods_or_services_to_people_in_india')
 est=profile.get('entity_establishments')
 if nexus is True: return True
 if isinstance(est,list) and any(str(x).strip().lower()=='india' for x in est): return True
 if isinstance(est,str) and 'india' in est.lower(): return True
 if nexus is False and est is not None: return False
 return None

def _evidence_for(rule_id,evidence):
 items=evidence.get(rule_id,[]) if isinstance(evidence,dict) else []
 return items if isinstance(items,list) else []

def _derive(rule, nexus, evidence_items, today):
 required=set(rule.get('required_evidence_types',[]))
 if rule['id']=='IN-DPDP-SCOPE':
  if nexus is None: return 'UNKNOWN'
  if nexus is False: return 'NOT_APPLICABLE'
 elif nexus is False:
  return 'NOT_APPLICABLE'
 elif nexus is None:
  return 'UNKNOWN'
 results=[str(x.get('result','')).upper() for x in evidence_items if isinstance(x,dict)]
 if any(x=='FAIL' for x in results): return 'FAIL'
 if any(x=='REVIEW' for x in results): return 'REVIEW'
 eff=_date(rule['effective'])
 future=eff is not None and today<eff
 if future: return 'FUTURE_EFFECTIVE'
 types={x.get('type') for x in evidence_items if isinstance(x,dict) and str(x.get('result','')).upper()=='PASS'}
 if required and required.issubset(types): return 'PASS'
 return 'UNKNOWN'

def dpdp(profile, evidence, base, today=None):
 pack=json.loads((base/'references/india-dpdp.json').read_text())
 today=today or dt.datetime.now(dt.timezone.utc).date()
 nexus=_india_nexus(profile)
 out=[]
 for c in pack['checks']:
  items=_evidence_for(c['id'],evidence)
  status=_derive(c,nexus,items,today)
  out.append({
   'rule_id':c['id'],'status':status,'severity':'unassessed','title':c['title'],
   'effective':c['effective'],'required_evidence_types':c.get('required_evidence_types',[]),
   'runtime_tests':c.get('runtime_tests',[]),'evidence_count':len(items),
   'next_step':c['verify']})
 return out

def scan(root,profile=None,evidence=None,today=None):
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
    if ms: findings.append({'rule_id':rid,'status':'REVIEW','severity':sev,'title':title,'path':rel,'lines':sorted({content.count('\n',0,m.start())+1 for m in ms})[:20],'confidence':'source-pattern-only','meaning':'Candidate signal; verify context before changing behavior.'})
 for rid,title,task in MANUAL:
  findings.append({'rule_id':rid,'status':'UNKNOWN','severity':'unassessed','title':title,'next_step':task})
 if profile is not None:
  findings.extend(dpdp(profile,evidence or {},Path(__file__).parents[1],today=today))
 return {
  'version':VERSION,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
  'mode':'source-config-questionnaire-runtime-evidence',
  'status_model':sorted(STATUSES),
  'overall':'INCOMPLETE_REVIEW_REQUIRED',
  'scope':{'files_scanned':scanned,'excluded_directories':sorted(SKIP),'extensions':sorted(EXTENSIONS),'max_file_bytes':LIMIT,'max_files':MAX_FILES,'omissions':omissions},
  'profile_provided':profile is not None,'evidence_provided':bool(evidence),
  'readiness_summary':readiness_summary(findings,today=today),
  'limitations':['No legal certification is performed.','Runtime PASS/FAIL requires user-supplied or tool-produced evidence; the CLI does not autonomously browse or operate third-party services.','FUTURE_EFFECTIVE is based on bundled dates and must be rechecked against current primary sources.','Source regex candidates can be false positives and are REVIEW, not violations.'],
  'findings':findings}

def _load_object(path,label):
 obj=json.loads(Path(path).read_text())
 if not isinstance(obj,dict): raise ValueError(label+' must be a JSON object.')
 return obj

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('root')
 ap.add_argument('--profile',help='Project profile JSON')
 ap.add_argument('--evidence',help='Evidence JSON mapping rule IDs to evidence records')
 ap.add_argument('--fail-on-review',action='store_true')
 args=ap.parse_args()
 try:
  profile=_load_object(args.profile,'Profile') if args.profile else None
  evidence=_load_object(args.evidence,'Evidence') if args.evidence else None
  if evidence is not None:
   validate_evidence(evidence)
  result=scan(args.root,profile,evidence)
 except (OSError,ValueError,json.JSONDecodeError):
  print(json.dumps({'error':'InvalidInput','message':'Invalid root, profile or evidence; no scan completed.'}),file=sys.stderr); return 2
 print(json.dumps(result,indent=2))
 return 1 if args.fail_on_review and any(f['status'] in {'REVIEW','FAIL'} for f in result['findings']) else 0
if __name__=='__main__': sys.exit(main())
