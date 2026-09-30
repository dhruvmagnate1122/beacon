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
  r=scan(self.root,{'offers_goods_or_services_to_people_in_india':None},today=dt.date(2028,1,1)); d=[f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')]
  self.assertTrue(d); self.assertTrue(all(f['status']=='UNKNOWN' for f in d))
 def test_not_applicable(self):
  r=scan(self.root,{'entity_establishments':['US'],'offers_goods_or_services_to_people_in_india':False},today=dt.date(2028,1,1)); d=[f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')]
  self.assertTrue(all(f['status']=='NOT_APPLICABLE' for f in d))
 def test_future_effective(self):
  r=scan(self.root,{'offers_goods_or_services_to_people_in_india':True},today=dt.date(2026,9,30)); d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-NOTICE']['status'],'FUTURE_EFFECTIVE'); self.assertEqual(d['IN-DPDP-CONSENT-MANAGER']['status'],'FUTURE_EFFECTIVE')
 def test_fail_beats_future(self):
  ev={'IN-DPDP-CONSENT-UX':[{'type':'runtime','result':'FAIL','details':'optional consent preselected'}]}
  r=scan(self.root,{'offers_goods_or_services_to_people_in_india':True},ev,today=dt.date(2026,9,30)); d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-CONSENT-UX']['status'],'FAIL')
 def test_pass_requires_all_evidence_types(self):
  ev={'IN-DPDP-CONSENT-UX':[{'type':x,'result':'PASS'} for x in ['source','config','runtime','legal']]}
  r=scan(self.root,{'offers_goods_or_services_to_people_in_india':True},ev,today=dt.date(2028,1,1)); d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-CONSENT-UX']['status'],'PASS')
 def test_partial_evidence_review(self):
  ev={'IN-DPDP-CONSENT':[{'type':'runtime','result':'REVIEW'}]}
  r=scan(self.root,{'offers_goods_or_services_to_people_in_india':True},ev,today=dt.date(2028,1,1)); d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')}
  self.assertEqual(d['IN-DPDP-CONSENT']['status'],'REVIEW')
 def test_cli_invalid_profile(self):
  script=str(Path(__file__).with_name('check.py')); profile=self.put('profile.json','[]')
  p=subprocess.run([sys.executable,script,str(self.root),'--profile',str(profile)],capture_output=True,text=True); self.assertEqual(p.returncode,2)
 def test_profile_schema(self):
  p=json.loads((Path(__file__).parents[1]/'assets/project-profile.json').read_text()); self.assertEqual(p['schema_version'],'0.2.0'); self.assertIn('consent_ui_default_state',p)
 def test_evidence_valid(self):
  self.assertEqual(validate_evidence({'IN-DPDP-CONSENT':[ev()]}),{'IN-DPDP-CONSENT':[ev()]})
 def test_evidence_accepts_reference_alias(self):
  item=ev(); item['reference']=item.pop('artifact'); validate_evidence({'IN-DPDP-CONSENT':[item]})
 def test_evidence_rejects_missing_key(self):
  bad=ev(); del bad['details']
  with self.assertRaises(ValueError): validate_evidence({'IN-DPDP-CONSENT':[bad]})
 def test_evidence_rejects_blank_locator(self):
  bad=ev(); bad['artifact']='  '
  with self.assertRaises(ValueError): validate_evidence({'IN-DPDP-CONSENT':[bad]})
 def test_evidence_rejects_bad_result(self):
  with self.assertRaises(ValueError): validate_evidence({'X':[ev('runtime','BOGUS')]})
 def test_evidence_rejects_foreign_status_vocabulary(self):
  for foreign in ('SUGGESTION','CLAIM_NEEDS_EVIDENCE'):
   with self.assertRaises(ValueError,msg=foreign): validate_evidence({'X':[ev('runtime',foreign)]})
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
  r=scan(self.root,{'offers_goods_or_services_to_people_in_india':True},e,today=dt.date(2026,9,30))
  s=r['readiness_summary']
  self.assertIn('IN-DPDP-CONSENT-UX',s['dpdp_fail'])
  self.assertIn('IN-DPDP-NOTICE',s['dpdp_future_effective'])
  self.assertEqual(sum(s['counts_by_status'].values()),len(r['findings']))
  self.assertIn('not a compliance determination',s['note'])

if __name__=='__main__': unittest.main()
