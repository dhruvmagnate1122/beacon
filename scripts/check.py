#!/usr/bin/env python3
"""Read-only launch triage plus evidence-driven jurisdiction readiness. Never a compliance certification."""
import argparse, datetime as dt, json, os, re, sys
from pathlib import Path

VERSION='0.7.0'
STATUSES={'PASS','FAIL','REVIEW','UNKNOWN','NOT_APPLICABLE','FUTURE_EFFECTIVE'}
SKIP={'.git','node_modules','.next','dist','build','.venv','venv','__pycache__','vendor','coverage'}
EXTENSIONS={'.js','.jsx','.ts','.tsx','.mjs','.cjs','.html','.css','.sql','.json','.py','.yml','.yaml','.toml'}
LIMIT=1024*1024; MAX_FILES=10000
PACK_FILES=('india-dpdp.json','eu-gdpr-eprivacy.json','uk-gdpr-pecr.json','us-federal-digital.json','india-certin.json','eu-digital-vat.json')
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

EVIDENCE_RESULTS={'PASS','FAIL','REVIEW'}
EVIDENCE_TYPES={'source','config','questionnaire','runtime','legal'}
PRODUCER_KINDS={'tool','external','manual'}

def validate_evidence(evidence, allowed_rule_ids=None):
 """Validate the reusable evidence contract before any readiness derivation."""
 if not isinstance(evidence,dict):
  raise ValueError('Evidence must be an object mapping rule IDs to record arrays.')
 for rid,items in evidence.items():
  if not isinstance(rid,str) or not rid.strip():
   raise ValueError('Evidence rule ID must be a non-empty string.')
  if allowed_rule_ids is not None and rid not in allowed_rule_ids:
   raise ValueError('Unknown evidence rule ID: '+rid)
  if not isinstance(items,list):
   raise ValueError('Evidence records for '+rid+' must be an array.')
  for idx,item in enumerate(items):
   prefix='Evidence record '+rid+'['+str(idx)+'] '
   if not isinstance(item,dict):
    raise ValueError(prefix+'must be an object.')
   for k in ('type','result','details','observed_at','environment','producer'):
    if k not in item:
     raise ValueError(prefix+'missing '+k)
   etype=str(item['type']).lower()
   if etype not in EVIDENCE_TYPES:
    raise ValueError(prefix+'has invalid type')
   item['type']=etype
   if str(item['result']).upper() not in EVIDENCE_RESULTS:
    raise ValueError(prefix+'has invalid result')
   if not isinstance(item['details'],str) or not item['details'].strip():
    raise ValueError(prefix+'requires non-empty details')
   if not isinstance(item['environment'],str) or not item['environment'].strip():
    raise ValueError(prefix+'requires non-empty environment')
   stamp=item['observed_at']
   if not isinstance(stamp,str) or not stamp.strip():
    raise ValueError(prefix+'requires observed_at')
   try:
    dt.datetime.fromisoformat(stamp.strip().replace('Z','+00:00'))
   except ValueError:
    raise ValueError(prefix+'has invalid observed_at')
   prod=item['producer']
   if (not isinstance(prod,dict) or prod.get('kind') not in PRODUCER_KINDS or
       not isinstance(prod.get('name'),str) or not prod.get('name').strip()):
    raise ValueError(prefix+'has invalid producer')
   artifact=item.get('artifact'); reference=item.get('reference')
   if not ((isinstance(artifact,str) and artifact.strip()) or
           (isinstance(reference,str) and reference.strip())):
    raise ValueError(prefix+'requires artifact or reference')
 return evidence

def _date(v):
 if v=='current': return None
 return dt.date.fromisoformat(v)

def _load_packs(base):
 packs={}
 for filename in PACK_FILES:
  p=json.loads((base/'references'/filename).read_text())
  pid=p.get('pack_id')
  if not isinstance(pid,str) or not pid:
   raise ValueError('Jurisdiction pack missing pack_id: '+filename)
  if pid in packs:
   raise ValueError('Duplicate jurisdiction pack ID: '+pid)
  if p.get('status_model')!=['PASS','FAIL','REVIEW','UNKNOWN','NOT_APPLICABLE','FUTURE_EFFECTIVE']:
   raise ValueError('Invalid status model in pack: '+pid)
  ids=[x.get('id') for x in p.get('checks',[])]
  if not ids or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):
   raise ValueError('Invalid or duplicate rule IDs in pack: '+pid)
  packs[pid]=p
 return packs

def _selected_pack_ids(profile,packs):
 if not profile: return []
 explicit=profile.get('jurisdiction_packs')
 if explicit is not None:
  if not isinstance(explicit,list) or any(not isinstance(x,str) for x in explicit):
   raise ValueError('jurisdiction_packs must be an array of pack IDs.')
  unknown=[x for x in explicit if x not in packs]
  if unknown: raise ValueError('Unknown jurisdiction pack: '+','.join(unknown))
  return list(dict.fromkeys(explicit))
 selected=[]
 for pid,p in packs.items():
  if any(profile.get(k) is not None for k in p.get('applicability_profile_fields',[])):
   selected.append(pid)
 return selected

def _india_applicability(profile):
 if not profile: return None
 if profile.get('all_relevant_processing_personal_or_domestic') is True:
  return False
 if profile.get('all_relevant_data_publicly_available_under_section_3c') is True:
  return False
 within=profile.get('processing_digital_personal_data_within_india')
 collected=profile.get('personal_data_collected_digitally_or_digitised_in_india')
 outside=profile.get('processing_digital_personal_data_outside_india')
 offered=profile.get('offers_goods_or_services_to_people_in_india')
 route_a=True if within is True and collected is True else (False if within is False or collected is False else None)
 route_b=True if outside is True and offered is True else (False if outside is False or offered is False else None)
 if route_a is True or route_b is True: return True
 if route_a is False and route_b is False: return False
 return None

def _eu_applicability(profile):
 if not profile: return None
 if profile.get('all_relevant_processing_purely_personal_or_household') is True:
  return False
 processes=profile.get('processes_personal_data')
 if processes is False: return False
 establishment=profile.get('processing_in_context_of_eu_eea_establishment')
 offering=profile.get('offers_goods_or_services_to_people_in_eu_eea')
 monitoring=profile.get('monitors_behavior_of_people_in_eu_eea')
 if processes is True and (establishment is True or offering is True or monitoring is True):
  return True
 if processes is True and establishment is False and offering is False and monitoring is False:
  return False
 return None

def _uk_gdpr_applicability(profile):
 if not profile: return None
 if profile.get('all_relevant_processing_purely_personal_or_household') is True:
  return False
 processes=profile.get('processes_personal_data')
 if processes is False: return False
 establishment=profile.get('processing_in_context_of_uk_establishment')
 offering=profile.get('offers_goods_or_services_to_people_in_uk')
 monitoring=profile.get('monitors_behavior_of_people_in_uk')
 public_intl=profile.get('uk_law_applies_by_public_international_law')
 if processes is True and (establishment is True or offering is True or monitoring is True or public_intl is True):
  return True
 if processes is True and establishment is False and offering is False and monitoring is False and public_intl is False:
  return False
 return None

def _uk_pecr_storage_applicability(profile):
 if not profile: return None
 uses=profile.get('uses_storage_or_access_technologies_for_uk_users')
 if uses is True: return True
 if uses is False: return False
 return None

def _uk_pecr_marketing_applicability(profile):
 if not profile: return None
 sends=profile.get('sends_electronic_direct_marketing_to_uk_recipients')
 if sends is True: return True
 if sends is False: return False
 return None

def _us_coppa_applicability(profile):
 if not profile: return None
 operates=profile.get('operates_website_or_online_service')
 child_directed=profile.get('us_service_directed_to_children_under_13')
 actual=profile.get('us_actual_knowledge_collects_from_child_under_13')
 third_party=profile.get('us_third_party_service_collects_on_child_directed_service')
 if operates is False and third_party is not True: return False
 if child_directed is True or actual is True or third_party is True: return True
 if operates is True and child_directed is False and actual is False and third_party is False: return False
 return None

def _us_canspam_applicability(profile):
 if not profile: return None
 sends=profile.get('sends_us_commercial_email')
 if sends is True: return True
 if sends is False: return False
 return None

def _us_dmca_applicability(profile):
 if not profile: return None
 relies=profile.get('relies_on_dmca_512_safe_harbor')
 if relies is True: return True
 if relies is False: return False
 return None

def _us_ada_web_applicability(profile):
 if not profile: return None
 public=profile.get('us_title_iii_public_accommodation')
 online=profile.get('website_or_app_offers_public_accommodation_goods_services')
 if public is True and online is True: return True
 if public is False or online is False: return False
 return None


def _us_coppa_applicability(profile):
 if not profile: return None
 collects=profile.get('coppa_collects_personal_information')
 child_directed=profile.get('coppa_child_directed_service')
 mixed=profile.get('coppa_mixed_audience_service')
 knowledge=profile.get('coppa_actual_knowledge_under13_collection')
 if collects is False: return False
 if collects is True and (child_directed is True or mixed is True or knowledge is True): return True
 if collects is True and child_directed is False and mixed is False and knowledge is False: return False
 return None

def _us_can_spam_applicability(profile):
 if not profile: return None
 sends=profile.get('sends_us_commercial_email')
 if sends is True: return True
 if sends is False: return False
 return None

def _us_dmca512c_applicability(profile):
 if not profile: return None
 hosted=profile.get('hosts_content_at_user_direction')
 seeks=profile.get('seeks_dmca_512c_safe_harbor')
 if hosted is True and seeks is True: return True
 if hosted is False or seeks is False: return False
 return None

def _us_ada_titleiii_applicability(profile):
 if not profile: return None
 covered=profile.get('us_ada_title_iii_public_accommodation')
 if covered is True: return True
 if covered is False: return False
 return None

def _us_ada_titleii_large_applicability(profile):
 if not profile: return None
 kind=profile.get('us_ada_title_ii_entity_size')
 if kind=='50000_or_more': return True
 if kind in {'under_50000_or_special_district','not_public_entity'}: return False
 return None

def _us_ada_titleii_small_applicability(profile):
 if not profile: return None
 kind=profile.get('us_ada_title_ii_entity_size')
 if kind=='under_50000_or_special_district': return True
 if kind in {'50000_or_more','not_public_entity'}: return False
 return None


def _certin_general_applicability(profile):
 if not profile: return None
 covered=profile.get('certin_general_directions_apply')
 if covered is True: return True
 if covered is False: return False
 return None

def _certin_incident_applicability(profile):
 if not profile: return None
 covered=profile.get('certin_incident_reporting_applies')
 if covered is True: return True
 if covered is False: return False
 return None

def _certin_provider_records_applicability(profile):
 if not profile: return None
 kind=profile.get('certin_provider_category')
 if kind in {'data_centre','vps','cloud_service','vpn_service'}: return True
 if kind=='not_applicable': return False
 return None

def _certin_virtual_asset_applicability(profile):
 if not profile: return None
 covered=profile.get('certin_virtual_asset_provider')
 if covered is True: return True
 if covered is False: return False
 return None


def _eu_vat_tbe_b2c_applicability(profile):
 if not profile: return None
 applies=profile.get('eu_vat_supplies_tbe_to_eu_consumers')
 if applies is True: return True
 if applies is False: return False
 return None

def _eu_vat_b2b_services_applicability(profile):
 if not profile: return None
 applies=profile.get('eu_vat_supplies_services_to_eu_businesses')
 if applies is True: return True
 if applies is False: return False
 return None

def _eu_vat_threshold_applicability(profile):
 if not profile: return None
 tbe=profile.get('eu_vat_supplies_tbe_to_eu_consumers')
 single=profile.get('eu_vat_supplier_established_in_single_member_state')
 if tbe is True and single is True: return True
 if tbe is False or single is False: return False
 return None

def _eu_vat_oss_applicability(profile):
 if not profile: return None
 uses=profile.get('eu_vat_uses_or_plans_oss_for_crossborder_b2c')
 if uses is True: return True
 if uses is False: return False
 return None

APPLICABILITY_MODELS={
 'india-dpdp-v1':_india_applicability,
 'eu-gdpr-v1':_eu_applicability,
 'uk-gdpr-v1':_uk_gdpr_applicability,
 'uk-pecr-storage-v1':_uk_pecr_storage_applicability,
 'uk-pecr-marketing-v1':_uk_pecr_marketing_applicability,
 'us-coppa-v1':_us_coppa_applicability,
 'us-can-spam-v1':_us_can_spam_applicability,
 'us-dmca512c-v1':_us_dmca512c_applicability,
 'us-ada-titleiii-v1':_us_ada_titleiii_applicability,
 'us-ada-titleii-large-v1':_us_ada_titleii_large_applicability,
 'us-ada-titleii-small-v1':_us_ada_titleii_small_applicability,
 'india-certin-general-v1':_certin_general_applicability,
 'india-certin-incident-v1':_certin_incident_applicability,
 'india-certin-provider-records-v1':_certin_provider_records_applicability,
 'india-certin-virtual-asset-v1':_certin_virtual_asset_applicability,
 'eu-vat-tbe-b2c-v1':_eu_vat_tbe_b2c_applicability,
 'eu-vat-b2b-services-v1':_eu_vat_b2b_services_applicability,
 'eu-vat-threshold-v1':_eu_vat_threshold_applicability,
 'eu-vat-oss-v1':_eu_vat_oss_applicability,
}

def _evidence_for(rule_id,evidence):
 items=evidence.get(rule_id,[]) if isinstance(evidence,dict) else []
 return items if isinstance(items,list) else []

def _derive(rule, applicability, evidence_items, today):
 required=set(rule.get('required_evidence_types',[]))
 if applicability is False:
  return 'NOT_APPLICABLE',None
 if applicability is None:
  return 'UNKNOWN',None
 results=[str(x.get('result','')).upper() for x in evidence_items if isinstance(x,dict)]
 if any(x=='FAIL' for x in results):
  readiness='FAIL'
 elif any(x=='REVIEW' for x in results):
  readiness='REVIEW'
 else:
  types={str(x.get('type','')).lower() for x in evidence_items if isinstance(x,dict) and str(x.get('result','')).upper()=='PASS'}
  readiness='PASS' if required and required.issubset(types) else 'UNKNOWN'
 eff=_date(rule['effective'])
 if eff is not None and today<eff:
  return 'FUTURE_EFFECTIVE',readiness
 return readiness,readiness

def _pack_today(pack,today):
 if today is not None: return today
 offset=int(pack.get('timezone_offset_minutes',0))
 return dt.datetime.now(dt.timezone(dt.timedelta(minutes=offset))).date()

def evaluate_pack(pack,profile,evidence,today=None):
 default_model=pack.get('applicability_model')
 if default_model not in APPLICABILITY_MODELS:
  raise ValueError('Unsupported applicability model: '+str(default_model))
 effective_today=_pack_today(pack,today)
 out=[]
 for rule in pack['checks']:
  model=rule.get('applicability_model',default_model)
  if model not in APPLICABILITY_MODELS:
   raise ValueError('Unsupported applicability model for '+rule['id']+': '+str(model))
  applicability=APPLICABILITY_MODELS[model](profile)
  items=_evidence_for(rule['id'],evidence)
  status,readiness=_derive(rule,applicability,items,effective_today)
  out.append({
   'rule_id':rule['id'],'pack_id':pack['pack_id'],'jurisdiction':pack.get('jurisdiction'),
   'applicability_model':model,
   'status':status,'readiness_status':readiness,'severity':'unassessed','title':rule['title'],
   'effective':rule['effective'],'required_evidence_types':rule.get('required_evidence_types',[]),
   'runtime_tests':rule.get('runtime_tests',[]),'evidence_count':len(items),
   'next_step':rule['verify']})
 return out

def readiness_summary(findings):
 counts={}; pack_summaries={}
 for f in findings:
  st=f.get('status'); counts[st]=counts.get(st,0)+1
  pid=f.get('pack_id')
  if not pid: continue
  s=pack_summaries.setdefault(pid,{
   'jurisdiction':f.get('jurisdiction'),'counts_by_status':{},
   'fail':[],'review':[],'future_effective':[],
   'future_readiness_fail':[],'future_readiness_review':[],'unknown_count':0})
  s['counts_by_status'][st]=s['counts_by_status'].get(st,0)+1
  rid=f.get('rule_id')
  if st=='FAIL': s['fail'].append(rid)
  elif st=='REVIEW': s['review'].append(rid)
  elif st=='FUTURE_EFFECTIVE':
   s['future_effective'].append(rid)
   if f.get('readiness_status')=='FAIL': s['future_readiness_fail'].append(rid)
   elif f.get('readiness_status')=='REVIEW': s['future_readiness_review'].append(rid)
  elif st=='UNKNOWN': s['unknown_count']+=1
 result={
  'counts_by_status':counts,
  'packs':pack_summaries,
  'note':'Mechanical rollup only; not a compliance determination. Recheck current primary sources before legal conclusions.'}
 india=pack_summaries.get('india-dpdp')
 if india:
  result.update({
   'dpdp_fail':india['fail'],'dpdp_review':india['review'],
   'dpdp_future_effective':india['future_effective'],
   'dpdp_future_readiness_fail':india['future_readiness_fail'],
   'dpdp_future_readiness_review':india['future_readiness_review'],
   'dpdp_unknown_count':india['unknown_count']})
 return result

def scan(root,profile=None,evidence=None,today=None):
 repo_base=Path(__file__).parents[1]
 packs=_load_packs(repo_base)
 selected=_selected_pack_ids(profile,packs)
 rule_to_pack={}
 for pid,p in packs.items():
  for rule in p['checks']:
   if rule['id'] in rule_to_pack:
    raise ValueError('Rule ID appears in multiple packs: '+rule['id'])
   rule_to_pack[rule['id']]=pid
 if evidence is not None:
  validate_evidence(evidence,allowed_rule_ids=set(rule_to_pack))
  if evidence and not selected:
   raise ValueError('Evidence requires an active jurisdiction pack in the project profile.')
  inactive=sorted({rule_to_pack[rid] for rid in evidence if rule_to_pack[rid] not in selected})
  if inactive:
   raise ValueError('Evidence supplied for inactive jurisdiction pack(s): '+','.join(inactive))

 root=Path(root).resolve()
 if not root.is_dir(): raise ValueError('Project root must be an existing directory.')
 findings=[]; omissions=[]; scanned=0
 for dirpath,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=sorted(d for d in dirs if d not in SKIP and not (Path(dirpath)/d).is_symlink())
  for name in sorted(files):
   path=Path(dirpath)/name; rel=path.relative_to(root).as_posix()
   if path.is_symlink(): omissions.append({'path':rel,'reason':'symlink not read'}); continue
   if path.suffix not in EXTENSIONS and not name.startswith('.env'): continue
   if scanned>=MAX_FILES: omissions.append({'path':rel,'reason':'file limit'}); continue
   try:
    if path.stat().st_size>LIMIT: omissions.append({'path':rel,'reason':'over 1 MiB limit'}); continue
    raw=path.read_bytes()
    if b'\0' in raw: raise ValueError('binary')
    file_content=raw.decode('utf-8')
   except (OSError,UnicodeError,ValueError): omissions.append({'path':rel,'reason':'unreadable or non-UTF-8 text'}); continue
   scanned+=1
   for rid,sev,title,pat in PATTERNS:
    ms=list(re.finditer(pat,file_content,re.I))
    if ms: findings.append({'rule_id':rid,'status':'REVIEW','severity':sev,'title':title,'path':rel,'lines':sorted({file_content.count('\n',0,m.start())+1 for m in ms})[:20],'confidence':'source-pattern-only','meaning':'Candidate signal; verify context before changing behavior.'})
 for rid,title,task in MANUAL:
  findings.append({'rule_id':rid,'status':'UNKNOWN','severity':'unassessed','title':title,'next_step':task})
 if profile is not None:
  for pid in selected:
   findings.extend(evaluate_pack(packs[pid],profile,evidence or {},today=today))
 return {
  'version':VERSION,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
  'mode':'source-config-questionnaire-runtime-evidence',
  'status_model':sorted(STATUSES),
  'overall':'INCOMPLETE_REVIEW_REQUIRED',
  'available_packs':sorted(packs),
  'active_packs':selected,
  'scope':{'files_scanned':scanned,'excluded_directories':sorted(SKIP),'extensions':sorted(EXTENSIONS),'max_file_bytes':LIMIT,'max_files':MAX_FILES,'omissions':omissions},
  'profile_provided':profile is not None,'evidence_provided':bool(evidence),
  'readiness_summary':readiness_summary(findings),
  'limitations':['No legal certification is performed.','Future-effective duties keep legal effective state separate from readiness evidence.','Runtime PASS/FAIL requires user-supplied or tool-produced evidence; the CLI does not autonomously browse or operate third-party services.','Jurisdiction packs require current primary-source review, including national implementation where relevant.','Source regex candidates can be false positives and are REVIEW, not violations.'],
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
  result=scan(args.root,profile,evidence)
 except (OSError,ValueError,json.JSONDecodeError):
  print(json.dumps({'error':'InvalidInput','message':'Invalid root, profile, pack selection or evidence; no scan completed.'}),file=sys.stderr); return 2
 print(json.dumps(result,indent=2))
 return 1 if args.fail_on_review and any(f['status'] in {'REVIEW','FAIL'} for f in result['findings']) else 0
if __name__=='__main__': sys.exit(main())
