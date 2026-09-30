import datetime as dt, json
from pathlib import Path
import subprocess, sys, tempfile, unittest
from check import scan, LIMIT, validate_evidence, readiness_summary

def ev(t='runtime',r='PASS'):
 return {'type':t,'result':r,'details':'synthetic check','observed_at':'2026-09-30T12:00:00Z',
  'environment':'staging','producer':{'kind':'manual','name':'reviewer'},'artifact':'run-7'}

class Checks(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
 def tearDown(self): self.tmp.cleanup()
 def put(self,n,t): p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);return p
 def ids(self): return {f['rule_id'] for f in scan(self.root)['findings'] if f['status']=='REVIEW'}
 def test_patterns(self):
  self.put('app.ts','const font="https://fonts.googleapis.com/css"; sessionReplay(); const NEXT_PUBLIC_SERVICE_ROLE_KEY="x";')
  self.put('schema.sql','ALTER TABLE users DISABLE ROW LEVEL SECURITY; CREATE POLICY p ON users USING (true);')
  self.assertEqual(self.ids(),{'PRIV-001','PRIV-002','SEC-002','DB-001','DB-002'})
 def test_redaction(self):
  key='sk_live_'+'SYNTHETIC'*4; self.put('.env','PAYMENT_KEY='+key); r=json.dumps(scan(self.root)); self.assertNotIn(key,r); self.assertIn('SEC-001',r)
 def test_empty_manual_unknown(self):
  r=scan(self.root); self.assertEqual(r['overall'],'INCOMPLETE_REVIEW_REQUIRED'); self.assertTrue(all(f['status']=='UNKNOWN' for f in r['findings']))
 def test_safe_source(self):
  self.put('app.ts','const key=process.env.SUPABASE_ANON_KEY;'); self.put('schema.sql','ALTER TABLE users ENABLE ROW LEVEL SECURITY; CREATE POLICY owner ON users USING (auth.uid() = user_id);'); self.assertEqual(self.ids(),set())
 def test_vendor_excluded(self): self.put('node_modules/test.js','sessionReplay()'); self.assertEqual(self.ids(),set())
 def test_symlink_and_oversized(self):
  outside=self.root.parent/(self.root.name+'-outside.txt'); outside.write_text('sessionReplay()')
  try:
   (self.root/'linked.ts').symlink_to(outside); self.put('big.ts','x'*(LIMIT+1))
   self.assertEqual(len(scan(self.root)['scope']['omissions']),2)
  finally: outside.unlink()
 def test_invalid_root(self):
  with self.assertRaises(ValueError): scan(self.root/'missing')
 def test_registry(self):
  rules=json.loads((Path(__file__).parents[1]/'references/rules.json').read_text())['rules']; self.assertEqual(len({r['id'] for r in rules}),len(rules))
 def test_dpdp_pack_schema(self):
  p=json.loads((Path(__file__).parents[1]/'references/india-dpdp.json').read_text()); ids=[x['id'] for x in p['checks']]
  self.assertEqual(len(ids),len(set(ids))); self.assertIn('IN-DPDP-CONSENT-UX',ids); self.assertEqual(p['status_model'],['PASS','FAIL','REVIEW','UNKNOWN','NOT_APPLICABLE','FUTURE_EFFECTIVE'])
 def test_unknown_nexus(self):
  r=scan(self.root,{'jurisdiction_packs':['india-dpdp'],'offers_goods_or_services_to_people_in_india':None},today=dt.date(2028,1,1)); d=[f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')]
  self.assertTrue(d); self.assertTrue(all(f['status']=='UNKNOWN' for f in d))
 def test_not_applicable(self):
  r=scan(self.root,{'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_within_india':False,'processing_digital_personal_data_outside_india':False,'offers_goods_or_services_to_people_in_india':False},today=dt.date(2028,1,1)); d=[f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')]
  self.assertTrue(all(f['status']=='NOT_APPLICABLE' for f in d))
 def test_future_effective(self):
  r=scan(self.root,{'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True},today=dt.date(2026,9,30)); d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-NOTICE']['status'],'FUTURE_EFFECTIVE'); self.assertEqual(d['IN-DPDP-CONSENT-MANAGER']['status'],'FUTURE_EFFECTIVE')
 def test_future_effective_keeps_readiness_fail(self):
  item=ev('runtime','FAIL'); item['details']='optional consent preselected'
  evidence={'IN-DPDP-CONSENT-UX':[item]}
  r=scan(self.root,{'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True},evidence,today=dt.date(2026,9,30)); d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-CONSENT-UX']['status'],'FUTURE_EFFECTIVE'); self.assertEqual(d['IN-DPDP-CONSENT-UX']['readiness_status'],'FAIL')
 def test_pass_requires_all_evidence_types(self):
  evidence={'IN-DPDP-CONSENT-UX':[ev(x,'PASS') for x in ['source','config','runtime','legal']]}
  r=scan(self.root,{'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True},evidence,today=dt.date(2028,1,1)); d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-CONSENT-UX']['status'],'PASS')
 def test_partial_evidence_review(self):
  evidence={'IN-DPDP-CONSENT':[ev('runtime','REVIEW')]}
  r=scan(self.root,{'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True},evidence,today=dt.date(2028,1,1)); d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-CONSENT']['status'],'REVIEW')
 def test_cli_invalid_profile(self):
  script=str(Path(__file__).with_name('check.py')); profile=self.put('profile.json','[]')
  p=subprocess.run([sys.executable,script,str(self.root),'--profile',str(profile)],capture_output=True,text=True); self.assertEqual(p.returncode,2)
 def test_profile_schema(self):
  p=json.loads((Path(__file__).parents[1]/'assets/project-profile.json').read_text()); self.assertEqual(p['schema_version'],'0.7.0'); self.assertIn('consent_ui_default_state',p); self.assertIn('processing_digital_personal_data_within_india',p)
 def test_evidence_valid(self):
  self.assertEqual(validate_evidence({'IN-DPDP-CONSENT':[ev()]}),{'IN-DPDP-CONSENT':[ev()]})
 def test_evidence_accepts_reference_alias(self):
  item=ev(); item['reference']=item.pop('artifact'); validate_evidence({'IN-DPDP-CONSENT':[item]})
 def test_evidence_accepts_case_insensitive_type(self):
  item=ev('Runtime','pass')
  result=validate_evidence({'IN-DPDP-CONSENT':[item]})
  self.assertEqual(result['IN-DPDP-CONSENT'][0]['type'],'runtime')
 def test_profile_drops_unused_outside_activity_field(self):
  p=json.loads((Path(__file__).parents[1]/'assets/project-profile.json').read_text())
  self.assertNotIn('processing_connected_with_activity_outside_india',p)
 def test_evidence_rejects_missing_key(self):
  bad=ev(); del bad['details']
  with self.assertRaises(ValueError): validate_evidence({'IN-DPDP-CONSENT':[bad]})
 def test_evidence_rejects_blank_locator(self):
  bad=ev(); bad['artifact']='  '
  with self.assertRaises(ValueError): validate_evidence({'IN-DPDP-CONSENT':[bad]})
 def test_evidence_rejects_bad_result(self):
  with self.assertRaises(ValueError): validate_evidence({'X':[ev('runtime','BOGUS')]})
 def test_evidence_rejects_foreign_status_vocabulary(self):
  for foreign in ('UNKNOWN','NOT_APPLICABLE','FUTURE_EFFECTIVE','SUGGESTION','CLAIM_NEEDS_EVIDENCE'):
   with self.assertRaises(ValueError,msg=foreign): validate_evidence({'X':[ev('runtime',foreign)]})
 def test_evidence_rejects_bad_type(self):
  with self.assertRaises(ValueError): validate_evidence({'X':[ev('browser','PASS')]})
 def test_evidence_rejects_blank_details(self):
  bad=ev(); bad['details']=' '
  with self.assertRaises(ValueError): validate_evidence({'X':[bad]})
 def test_evidence_rejects_blank_environment(self):
  bad=ev(); bad['environment']=''
  with self.assertRaises(ValueError): validate_evidence({'X':[bad]})
 def test_evidence_rejects_bad_timestamp(self):
  bad=ev(); bad['observed_at']='not-a-time'
  with self.assertRaises(ValueError): validate_evidence({'X':[bad]})
 def test_scan_validates_evidence_programmatically(self):
  bad=ev(); bad['artifact']=''
  with self.assertRaises(ValueError): scan(self.root,{}, {'X':[bad]})
 def test_evidence_rejects_bad_producer(self):
  bad=ev(); bad['producer']={'kind':'ouija','name':'x'}
  with self.assertRaises(ValueError): validate_evidence({'X':[bad]})
 def test_evidence_must_be_object(self):
  with self.assertRaises(ValueError): validate_evidence([ev()])
 def test_cli_invalid_evidence(self):
  script=str(Path(__file__).with_name('check.py')); bad=self.put('evidence.json','{"X":"not-a-list"}')
  p=subprocess.run([sys.executable,script,str(self.root),'--evidence',str(bad)],capture_output=True,text=True); self.assertEqual(p.returncode,2)
 def test_readiness_summary(self):
  full=dict(ev('runtime','FAIL')); full['reference']=full.pop('artifact')
  e={'IN-DPDP-CONSENT-UX':[full]}
  r=scan(self.root,{'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True},e,today=dt.date(2026,9,30))
  s=r['readiness_summary']
  self.assertIn('IN-DPDP-CONSENT-UX',s['dpdp_future_effective'])
  self.assertIn('IN-DPDP-CONSENT-UX',s['dpdp_future_readiness_fail'])
  self.assertIn('IN-DPDP-NOTICE',s['dpdp_future_effective'])
  self.assertEqual(sum(s['counts_by_status'].values()),len(r['findings']))
  self.assertIn('not a compliance determination',s['note'])

 def test_evidence_rejects_unknown_rule_id(self):
  with self.assertRaises(ValueError): scan(self.root,{}, {'IN-DPDP-CONSET':[ev()]})
 def test_india_scope_unknown_when_facts_partial(self):
  r=scan(self.root,{'jurisdiction_packs':['india-dpdp'],'offers_goods_or_services_to_people_in_india':False},today=dt.date(2028,1,1))
  d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertTrue(all(x['status']=='UNKNOWN' for x in d.values()))
 def test_india_scope_within_india_route(self):
  profile={'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_within_india':True,'personal_data_collected_digitally_or_digitised_in_india':True}
  r=scan(self.root,profile,today=dt.date(2028,1,1))
  d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-NOTICE']['status'],'UNKNOWN')
 def test_india_scope_exclusion(self):
  profile={'jurisdiction_packs':['india-dpdp'],'all_relevant_processing_personal_or_domestic':True}
  r=scan(self.root,profile,today=dt.date(2028,1,1))
  d=[f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')]
  self.assertTrue(all(x['status']=='NOT_APPLICABLE' for x in d))
 def test_effective_date_boundary(self):
  profile={'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True}
  r=scan(self.root,profile,today=dt.date(2027,5,13))
  d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertNotEqual(d['IN-DPDP-NOTICE']['status'],'FUTURE_EFFECTIVE')
 def test_future_pass_preserves_effective_state(self):
  evidence={'IN-DPDP-CONSENT-UX':[ev(x,'PASS') for x in ['source','config','runtime','legal']]}
  profile={'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True}
  r=scan(self.root,profile,evidence,today=dt.date(2026,9,30))
  d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-CONSENT-UX']['status'],'FUTURE_EFFECTIVE')
  self.assertEqual(d['IN-DPDP-CONSENT-UX']['readiness_status'],'PASS')

 def test_eu_pack_schema(self):
  p=json.loads((Path(__file__).parents[1]/'references/eu-gdpr-eprivacy.json').read_text()); ids=[x['id'] for x in p['checks']]
  self.assertEqual(p['pack_id'],'eu-gdpr-eprivacy'); self.assertEqual(len(ids),len(set(ids))); self.assertIn('EU-GDPR-SCOPE',ids); self.assertIn('EU-EPRIVACY-TRACKING',ids)
 def test_explicit_pack_selection(self):
  profile={'jurisdiction_packs':['eu-gdpr-eprivacy'],'processes_personal_data':True,'offers_goods_or_services_to_people_in_eu_eea':True}
  r=scan(self.root,profile)
  self.assertEqual(r['active_packs'],['eu-gdpr-eprivacy'])
  ids={f['rule_id'] for f in r['findings']}
  self.assertIn('EU-GDPR-SCOPE',ids); self.assertNotIn('IN-DPDP-SCOPE',ids)
 def test_eu_scope_applies_outside_eu_when_offering(self):
  profile={'jurisdiction_packs':['eu-gdpr-eprivacy'],'processes_personal_data':True,'processing_in_context_of_eu_eea_establishment':False,'offers_goods_or_services_to_people_in_eu_eea':True,'monitors_behavior_of_people_in_eu_eea':False}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='eu-gdpr-eprivacy'}
  self.assertTrue(d); self.assertTrue(all(x['status']=='UNKNOWN' for x in d.values()))
 def test_eu_scope_not_applicable_when_all_routes_ruled_out(self):
  profile={'jurisdiction_packs':['eu-gdpr-eprivacy'],'processes_personal_data':True,'processing_in_context_of_eu_eea_establishment':False,'offers_goods_or_services_to_people_in_eu_eea':False,'monitors_behavior_of_people_in_eu_eea':False}
  r=scan(self.root,profile)
  d=[f for f in r['findings'] if f.get('pack_id')=='eu-gdpr-eprivacy']
  self.assertTrue(d); self.assertTrue(all(x['status']=='NOT_APPLICABLE' for x in d))
 def test_eu_consent_fail(self):
  profile={'jurisdiction_packs':['eu-gdpr-eprivacy'],'processes_personal_data':True,'offers_goods_or_services_to_people_in_eu_eea':True}
  evidence={'EU-GDPR-CONSENT':[ev('runtime','FAIL')]}
  r=scan(self.root,profile,evidence)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='eu-gdpr-eprivacy'}
  self.assertEqual(d['EU-GDPR-CONSENT']['status'],'FAIL')
 def test_inactive_pack_evidence_rejected(self):
  profile={'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True}
  with self.assertRaises(ValueError): scan(self.root,profile,{'EU-GDPR-CONSENT':[ev('runtime','FAIL')]})
 def test_two_packs_together(self):
  profile={'jurisdiction_packs':['india-dpdp','eu-gdpr-eprivacy'],
   'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True,
   'processes_personal_data':True,'offers_goods_or_services_to_people_in_eu_eea':True}
  r=scan(self.root,profile,today=dt.date(2028,1,1))
  self.assertEqual(r['active_packs'],['india-dpdp','eu-gdpr-eprivacy'])
  self.assertIn('india-dpdp',r['readiness_summary']['packs']); self.assertIn('eu-gdpr-eprivacy',r['readiness_summary']['packs'])
 def test_unknown_pack_rejected(self):
  with self.assertRaises(ValueError): scan(self.root,{'jurisdiction_packs':['mars-law']})
 def test_evidence_without_active_pack_rejected(self):
  with self.assertRaises(ValueError): scan(self.root,None,{'EU-GDPR-CONSENT':[ev()]})

 def test_uk_pack_schema(self):
  p=json.loads((Path(__file__).parents[1]/'references/uk-gdpr-pecr.json').read_text()); ids=[x['id'] for x in p['checks']]
  self.assertEqual(p['pack_id'],'uk-gdpr-pecr'); self.assertEqual(len(ids),len(set(ids)))
  self.assertIn('UK-GDPR-SCOPE',ids); self.assertIn('UK-PECR-STORAGE',ids); self.assertIn('UK-PECR-MARKETING',ids)
 def test_uk_gdpr_scope_applies_when_targeting(self):
  profile={'jurisdiction_packs':['uk-gdpr-pecr'],'processes_personal_data':True,
   'processing_in_context_of_uk_establishment':False,'offers_goods_or_services_to_people_in_uk':True,
   'monitors_behavior_of_people_in_uk':False,'uk_law_applies_by_public_international_law':False,
   'uses_storage_or_access_technologies_for_uk_users':False,'sends_electronic_direct_marketing_to_uk_recipients':False}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='uk-gdpr-pecr'}
  self.assertEqual(d['UK-GDPR-SCOPE']['status'],'UNKNOWN')
  self.assertEqual(d['UK-PECR-STORAGE']['status'],'NOT_APPLICABLE')
  self.assertEqual(d['UK-PECR-MARKETING']['status'],'NOT_APPLICABLE')
 def test_uk_pecr_storage_has_independent_applicability(self):
  profile={'jurisdiction_packs':['uk-gdpr-pecr'],'processes_personal_data':False,
   'processing_in_context_of_uk_establishment':False,'offers_goods_or_services_to_people_in_uk':False,
   'monitors_behavior_of_people_in_uk':False,'uk_law_applies_by_public_international_law':False,
   'uses_storage_or_access_technologies_for_uk_users':True,'sends_electronic_direct_marketing_to_uk_recipients':False}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='uk-gdpr-pecr'}
  self.assertEqual(d['UK-GDPR-SCOPE']['status'],'NOT_APPLICABLE')
  self.assertEqual(d['UK-PECR-STORAGE']['status'],'UNKNOWN')
  self.assertEqual(d['UK-PECR-STORAGE']['applicability_model'],'uk-pecr-storage-v1')
 def test_uk_pecr_marketing_has_independent_applicability(self):
  profile={'jurisdiction_packs':['uk-gdpr-pecr'],'processes_personal_data':False,
   'processing_in_context_of_uk_establishment':False,'offers_goods_or_services_to_people_in_uk':False,
   'monitors_behavior_of_people_in_uk':False,'uk_law_applies_by_public_international_law':False,
   'uses_storage_or_access_technologies_for_uk_users':False,'sends_electronic_direct_marketing_to_uk_recipients':True}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='uk-gdpr-pecr'}
  self.assertEqual(d['UK-PECR-MARKETING']['status'],'UNKNOWN')
  self.assertEqual(d['UK-PECR-MARKETING']['applicability_model'],'uk-pecr-marketing-v1')
 def test_uk_pecr_fail_does_not_force_uk_gdpr(self):
  profile={'jurisdiction_packs':['uk-gdpr-pecr'],'processes_personal_data':False,
   'processing_in_context_of_uk_establishment':False,'offers_goods_or_services_to_people_in_uk':False,
   'monitors_behavior_of_people_in_uk':False,'uk_law_applies_by_public_international_law':False,
   'uses_storage_or_access_technologies_for_uk_users':True,'sends_electronic_direct_marketing_to_uk_recipients':False}
  evidence={'UK-PECR-STORAGE':[ev('runtime','FAIL')]}
  r=scan(self.root,profile,evidence)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='uk-gdpr-pecr'}
  self.assertEqual(d['UK-PECR-STORAGE']['status'],'FAIL')
  self.assertEqual(d['UK-GDPR-SCOPE']['status'],'NOT_APPLICABLE')
 def test_three_packs_together(self):
  profile={'jurisdiction_packs':['india-dpdp','eu-gdpr-eprivacy','uk-gdpr-pecr'],
   'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True,
   'processes_personal_data':True,'offers_goods_or_services_to_people_in_eu_eea':True,
   'processing_in_context_of_uk_establishment':False,'offers_goods_or_services_to_people_in_uk':True,
   'monitors_behavior_of_people_in_uk':False,'uk_law_applies_by_public_international_law':False,
   'uses_storage_or_access_technologies_for_uk_users':True,'sends_electronic_direct_marketing_to_uk_recipients':True}
  r=scan(self.root,profile,today=dt.date(2028,1,1))
  self.assertEqual(r['active_packs'],['india-dpdp','eu-gdpr-eprivacy','uk-gdpr-pecr'])
  self.assertIn('uk-gdpr-pecr',r['readiness_summary']['packs'])

 def test_us_pack_schema(self):
  p=json.loads((Path(__file__).parents[1]/'references/us-federal-digital.json').read_text()); ids=[x['id'] for x in p['checks']]
  self.assertEqual(p['pack_id'],'us-federal-digital'); self.assertEqual(len(ids),len(set(ids)))
  self.assertIn('US-COPPA-SCOPE',ids); self.assertIn('US-CANSPAM',ids); self.assertIn('US-DMCA512C-AGENT',ids); self.assertIn('US-ADA-T3-WEB',ids)
 def test_us_coppa_independent_applicability(self):
  profile={'jurisdiction_packs':['us-federal-digital'],'coppa_collects_personal_information':True,
   'coppa_child_directed_service':True,'coppa_mixed_audience_service':False,'coppa_actual_knowledge_under13_collection':False,
   'sends_us_commercial_email':False,'hosts_content_at_user_direction':False,'seeks_dmca_512c_safe_harbor':False,
   'us_ada_title_iii_public_accommodation':False,'us_ada_title_ii_entity_size':'not_public_entity'}
  r=scan(self.root,profile,today=dt.date(2026,10,1))
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='us-federal-digital'}
  self.assertEqual(d['US-COPPA-SCOPE']['status'],'UNKNOWN')
  self.assertEqual(d['US-CANSPAM']['status'],'NOT_APPLICABLE')
  self.assertEqual(d['US-DMCA512C-AGENT']['status'],'NOT_APPLICABLE')
 def test_us_can_spam_independent_applicability(self):
  profile={'jurisdiction_packs':['us-federal-digital'],'coppa_collects_personal_information':False,
   'coppa_child_directed_service':False,'coppa_mixed_audience_service':False,'coppa_actual_knowledge_under13_collection':False,
   'sends_us_commercial_email':True,'hosts_content_at_user_direction':False,'seeks_dmca_512c_safe_harbor':False,
   'us_ada_title_iii_public_accommodation':False,'us_ada_title_ii_entity_size':'not_public_entity'}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='us-federal-digital'}
  self.assertEqual(d['US-CANSPAM']['status'],'UNKNOWN')
  self.assertEqual(d['US-COPPA-SCOPE']['status'],'NOT_APPLICABLE')
 def test_us_dmca_independent_applicability(self):
  profile={'jurisdiction_packs':['us-federal-digital'],'coppa_collects_personal_information':False,
   'coppa_child_directed_service':False,'coppa_mixed_audience_service':False,'coppa_actual_knowledge_under13_collection':False,
   'sends_us_commercial_email':False,'hosts_content_at_user_direction':True,'seeks_dmca_512c_safe_harbor':True,
   'us_ada_title_iii_public_accommodation':False,'us_ada_title_ii_entity_size':'not_public_entity'}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='us-federal-digital'}
  self.assertEqual(d['US-DMCA512C-AGENT']['status'],'UNKNOWN')
  self.assertEqual(d['US-CANSPAM']['status'],'NOT_APPLICABLE')
 def test_us_ada_titleii_future_dates(self):
  profile={'jurisdiction_packs':['us-federal-digital'],'coppa_collects_personal_information':False,
   'coppa_child_directed_service':False,'coppa_mixed_audience_service':False,'coppa_actual_knowledge_under13_collection':False,
   'sends_us_commercial_email':False,'hosts_content_at_user_direction':False,'seeks_dmca_512c_safe_harbor':False,
   'us_ada_title_iii_public_accommodation':False,'us_ada_title_ii_entity_size':'50000_or_more'}
  r=scan(self.root,profile,today=dt.date(2026,10,1))
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='us-federal-digital'}
  self.assertEqual(d['US-ADA-T2-LARGE-WEB']['status'],'FUTURE_EFFECTIVE')
  self.assertEqual(d['US-ADA-T2-SMALL-WEB']['status'],'NOT_APPLICABLE')
 def test_us_evidence_isolated_from_other_packs(self):
  profile={'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True}
  with self.assertRaises(ValueError): scan(self.root,profile,{'US-CANSPAM':[ev('runtime','FAIL')]})

 def test_certin_pack_schema(self):
  p=json.loads((Path(__file__).parents[1]/'references/india-certin.json').read_text()); ids=[x['id'] for x in p['checks']]
  self.assertEqual(p['pack_id'],'india-certin'); self.assertEqual(len(ids),len(set(ids)))
  self.assertIn('IN-CERTIN-INCIDENT-6H',ids); self.assertIn('IN-CERTIN-LOGS-180D',ids)
 def test_certin_general_and_incident_applicability(self):
  profile={'jurisdiction_packs':['india-certin'],'certin_general_directions_apply':True,
   'certin_incident_reporting_applies':True,'certin_provider_category':'not_applicable','certin_virtual_asset_provider':False}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='india-certin'}
  self.assertEqual(d['IN-CERTIN-NTP']['status'],'UNKNOWN')
  self.assertEqual(d['IN-CERTIN-INCIDENT-6H']['status'],'UNKNOWN')
  self.assertEqual(d['IN-CERTIN-PROVIDER-RECORDS']['status'],'NOT_APPLICABLE')
 def test_certin_provider_records_independent_applicability(self):
  profile={'jurisdiction_packs':['india-certin'],'certin_general_directions_apply':False,
   'certin_incident_reporting_applies':False,'certin_provider_category':'cloud_service','certin_virtual_asset_provider':False}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='india-certin'}
  self.assertEqual(d['IN-CERTIN-SCOPE']['status'],'NOT_APPLICABLE')
  self.assertEqual(d['IN-CERTIN-PROVIDER-RECORDS']['status'],'UNKNOWN')
 def test_certin_virtual_asset_independent_applicability(self):
  profile={'jurisdiction_packs':['india-certin'],'certin_general_directions_apply':False,
   'certin_incident_reporting_applies':False,'certin_provider_category':'not_applicable','certin_virtual_asset_provider':True}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='india-certin'}
  self.assertEqual(d['IN-CERTIN-VIRTUAL-ASSET-RECORDS']['status'],'UNKNOWN')
 def test_certin_evidence_isolated(self):
  profile={'jurisdiction_packs':['india-dpdp'],'processing_digital_personal_data_outside_india':True,'offers_goods_or_services_to_people_in_india':True}
  with self.assertRaises(ValueError): scan(self.root,profile,{'IN-CERTIN-LOGS-180D':[ev('runtime','FAIL')]})

 def test_eu_vat_pack_schema(self):
  p=json.loads((Path(__file__).parents[1]/'references/eu-digital-vat.json').read_text()); ids=[x['id'] for x in p['checks']]
  self.assertEqual(p['pack_id'],'eu-digital-vat'); self.assertEqual(len(ids),len(set(ids)))
  self.assertIn('EU-VAT-B2C-TBE-PLACE',ids); self.assertIn('EU-VAT-10K-THRESHOLD',ids); self.assertIn('EU-VAT-OSS',ids)
 def test_eu_vat_tbe_and_b2b_independent_applicability(self):
  profile={'jurisdiction_packs':['eu-digital-vat'],'eu_vat_supplies_tbe_to_eu_consumers':True,
   'eu_vat_supplies_services_to_eu_businesses':False,'eu_vat_supplier_established_in_single_member_state':True,
   'eu_vat_uses_or_plans_oss_for_crossborder_b2c':False}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='eu-digital-vat'}
  self.assertEqual(d['EU-VAT-B2C-TBE-PLACE']['status'],'UNKNOWN')
  self.assertEqual(d['EU-VAT-B2B-SERVICES']['status'],'NOT_APPLICABLE')
 def test_eu_vat_threshold_requires_single_member_state(self):
  profile={'jurisdiction_packs':['eu-digital-vat'],'eu_vat_supplies_tbe_to_eu_consumers':True,
   'eu_vat_supplies_services_to_eu_businesses':False,'eu_vat_supplier_established_in_single_member_state':False,
   'eu_vat_uses_or_plans_oss_for_crossborder_b2c':False}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='eu-digital-vat'}
  self.assertEqual(d['EU-VAT-10K-THRESHOLD']['status'],'NOT_APPLICABLE')
  self.assertEqual(d['EU-VAT-B2C-TBE-PLACE']['status'],'UNKNOWN')
 def test_eu_vat_oss_independent_applicability(self):
  profile={'jurisdiction_packs':['eu-digital-vat'],'eu_vat_supplies_tbe_to_eu_consumers':False,
   'eu_vat_supplies_services_to_eu_businesses':False,'eu_vat_supplier_established_in_single_member_state':False,
   'eu_vat_uses_or_plans_oss_for_crossborder_b2c':True}
  r=scan(self.root,profile)
  d={f['rule_id']:f for f in r['findings'] if f.get('pack_id')=='eu-digital-vat'}
  self.assertEqual(d['EU-VAT-OSS']['status'],'UNKNOWN')
  self.assertEqual(d['EU-VAT-SCOPE']['status'],'NOT_APPLICABLE')
 def test_eu_vat_evidence_isolated(self):
  profile={'jurisdiction_packs':['eu-gdpr-eprivacy'],'processes_personal_data':True,'offers_goods_or_services_to_people_in_eu_eea':True}
  with self.assertRaises(ValueError): scan(self.root,profile,{'EU-VAT-OSS':[ev('runtime','FAIL')]})

if __name__=='__main__': unittest.main()
