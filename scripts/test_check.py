import json
from pathlib import Path
import subprocess, sys, tempfile, unittest
from check import scan, LIMIT
class Checks(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
 def tearDown(self): self.tmp.cleanup()
 def put(self,n,t): p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);return p
 def ids(self): return {f['rule_id'] for f in scan(self.root)['findings'] if f['status']=='review'}
 def test_patterns(self):
  self.put('app.ts','const font="https://fonts.googleapis.com/css"; sessionReplay(); const NEXT_PUBLIC_SERVICE_ROLE_KEY="x";');self.put('schema.sql','ALTER TABLE users DISABLE ROW LEVEL SECURITY; CREATE POLICY p ON users USING (true);');self.assertEqual(self.ids(),{'PRIV-001','PRIV-002','SEC-002','DB-001','DB-002'})
 def test_redaction(self):
  key='sk_live_'+'SYNTHETIC'*4;self.put('.env','PAYMENT_KEY='+key);r=json.dumps(scan(self.root));self.assertNotIn(key,r);self.assertIn('SEC-001',r)
 def test_empty_is_unknown(self):
  r=scan(self.root);self.assertEqual(r['overall'],'incomplete-review-required');self.assertTrue(all(f['status']=='unknown' for f in r['findings']))
 def test_safe_source(self):
  self.put('app.ts','const key=process.env.SUPABASE_ANON_KEY;');self.put('schema.sql','ALTER TABLE users ENABLE ROW LEVEL SECURITY; CREATE POLICY owner ON users USING (auth.uid() = user_id);');self.assertEqual(self.ids(),set())
 def test_vendor_excluded(self): self.put('node_modules/test.js','sessionReplay()');self.assertEqual(self.ids(),set())
 def test_symlinks_not_read(self):
  outside=self.root.parent/(self.root.name+'-outside.txt');outside.write_text('sessionReplay()')
  try: (self.root/'linked.ts').symlink_to(outside);self.assertEqual(self.ids(),set());self.assertEqual(len(scan(self.root)['scope']['omissions']),1)
  finally: outside.unlink()
 def test_oversized_and_binary(self): self.put('big.ts','x'*(LIMIT+1));(self.root/'bin.js').write_bytes(b'\0sessionReplay');self.assertEqual(len(scan(self.root)['scope']['omissions']),2)
 def test_candidate_not_violation(self): self.put('comments.sql','-- DISABLE ROW LEVEL SECURITY in an example');f=scan(self.root)['findings'][0];self.assertEqual(f['status'],'review');self.assertEqual(f['lines'],[1])
 def test_invalid_root(self):
  with self.assertRaises(ValueError): scan(self.root/'missing')
 def test_cli(self):
  script=str(Path(__file__).with_name('check.py'));self.put('app.ts','sessionReplay()');p=subprocess.run([sys.executable,script,str(self.root),'--fail-on-review'],capture_output=True,text=True);self.assertEqual(p.returncode,1);json.loads(p.stdout);profile=self.put('profile.json','[]');p=subprocess.run([sys.executable,script,str(self.root),'--profile',str(profile)],capture_output=True,text=True);self.assertEqual(p.returncode,2)
 def test_registry(self):
  rules=json.loads((Path(__file__).parents[1]/'references/rules.json').read_text())['rules'];self.assertEqual(len({r['id'] for r in rules}),len(rules));self.assertTrue(all(r['source_url'].startswith('https://') and r['reviewer'] is None for r in rules))
 def test_dpdp_pack_unique(self):
  p=json.loads((Path(__file__).parents[1]/'references/india-dpdp.json').read_text());ids=[x['id'] for x in p['checks']];self.assertEqual(len(ids),len(set(ids)));self.assertEqual(p['pack_version'],'0.2.0')
 def test_dpdp_india_profile(self):
  r=scan(self.root,{'offers_goods_or_services_to_people_in_india':True});d={f['rule_id']:f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')};self.assertEqual(d['IN-DPDP-SCOPE']['status'],'unknown');self.assertEqual(d['IN-DPDP-NOTICE']['status'],'future-effective');self.assertEqual(d['IN-DPDP-CONSENT-MANAGER']['effective'],'2026-11-13')
 def test_dpdp_unknown_nexus(self):
  r=scan(self.root,{'offers_goods_or_services_to_people_in_india':None});d=[f for f in r['findings'] if f['rule_id'].startswith('IN-DPDP')];self.assertTrue(d);self.assertTrue(all(f['status']=='applicability-unknown' for f in d))
 def test_profile_schema(self):
  p=json.loads((Path(__file__).parents[1]/'assets/project-profile.json').read_text());self.assertEqual(p['schema_version'],'0.2.0');self.assertIn('breach_detection_response_and_notification_plan',p)
if __name__=='__main__': unittest.main()
