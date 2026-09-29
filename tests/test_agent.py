import json
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from afteraction.config import Config
from afteraction.domain import lesson, redact
from afteraction.service import Agent
from afteraction.sample import CURRENT, EPISODES
from afteraction.memory import MemoryUnavailable
from afteraction.server import create_server


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config = Config(db=str(Path(self.tmp.name)/'test.db'))
        self.agent = Agent(self.config)

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_abstains(self):
        r = self.agent.investigate(CURRENT)
        self.assertFalse(r['decision']['proposed'])
        self.assertFalse(r['decision']['eligible'])

    def test_learning_changes_decision(self):
        self.agent.seed()
        r = self.agent.investigate(CURRENT)['decision']
        self.assertEqual(r['avoided'][0]['sources'], ['AA-demo-001'])
        self.assertEqual(r['proposed'][0]['sources'], ['AA-demo-002'])
        self.assertEqual(len(r['excluded']), 1)

    def test_scope_change_withholds_old_fixes(self):
        self.agent.seed()
        for patch in ({'architecture':'pgbouncer'}, {'service':'other-service'}, {'environment':'development'}):
            self.assertFalse(self.agent.investigate({**CURRENT, **patch})['decision']['eligible'])

    def test_new_context_learns(self):
        self.agent.seed()
        data = {**EPISODES[1], 'architecture':'pgbouncer', 'confirmed':True}
        row = self.agent.record(data)['lesson']
        r = self.agent.investigate({**CURRENT, 'architecture':'pgbouncer'})['decision']
        self.assertEqual([x['id'] for x in r['eligible']], [row['id']])

    def test_conflict_abstains(self):
        self.agent.seed()
        self.agent.record({**EPISODES[1], 'outcome':'failed', 'confirmed':True})
        d = self.agent.investigate(CURRENT)['decision']
        self.assertFalse(d['proposed'])
        self.assertEqual(len(d['conflicts']), 1)
        self.assertEqual(len(d['conflicts'][0]['sources']), 2)

    def test_retirement(self):
        self.agent.seed()
        self.agent.store.retire('AA-demo-002')
        self.assertFalse(self.agent.investigate(CURRENT)['decision']['proposed'])

    def test_persistence_and_idempotent_seed(self):
        self.agent.seed()
        another = Agent(self.config)
        another.seed()
        self.assertEqual(len(another.store.rows()), 3)
        self.assertTrue(another.investigate(CURRENT)['decision']['avoided'])

    def test_baseline_does_not_read_memory(self):
        self.agent.seed()
        n = len(self.agent.store.traces())
        self.agent.investigate({**CURRENT, 'use_memory':False})
        self.assertEqual(n, len(self.agent.store.traces()))

    def test_review_required(self):
        with self.assertRaises(ValueError): self.agent.record(EPISODES[0])
        self.assertFalse(self.agent.store.rows())

    def test_invalid_outcome_date_and_scope(self):
        for update in ({'outcome':'probably'}, {'observed_at':'2099-01-01T00:00:00Z'}, {'observed_at':'2026-01-01'}, {'service':'x/../../'}, {'reason':''}):
            with self.assertRaises(ValueError): lesson({**EPISODES[0], **update})

    def test_redaction_before_storage(self):
        row = self.agent.record({**EPISODES[0], 'reason':'password=hunter2 api_key=abc Authorization: Bearer xyz', 'confirmed':True})['lesson']
        for secret in ('hunter2', 'abc', 'xyz'): self.assertNotIn(secret, row['reason'])


class FakeHindsight(BaseHTTPRequestHandler):
    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.calls.append((self.path, payload))
        status, body = 200, {}
        if self.server.fail:
            status, body = 503, {'secret':'DO NOT LEAK'}
        elif self.path.endswith('/memories'):
            self.server.saved[payload['items'][0]['document_id']] = payload['items'][0]
            body = {'success':True}
        elif self.path.endswith('/recall'):
            body = {'results':[{'id':'fact-'+key, 'text':'Extracted outcome', 'context':value['context']} for key,value in self.server.saved.items() if all(t in value['tags'] for t in payload['tags'])]}
        elif self.path.endswith('/reflect'):
            body = {'text':'Check connection pressure; consult the original outcome record.', 'based_on':{'memories':[]}}
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())
    def log_message(self,*args): pass


class LiveAdapterTests(AgentTests):
    # Reuse setup only, not rehearsal tests (defined explicitly below).
    def setUp(self):
        super().setUp()
        self.fake = ThreadingHTTPServer(('127.0.0.1',0), FakeHindsight)
        self.fake.calls, self.fake.saved, self.fake.fail = [], {}, False
        self.thread = threading.Thread(target=self.fake.serve_forever, daemon=True)
        self.thread.start()
        self.config.mode='hindsight'
        self.config.url=f'http://127.0.0.1:{self.fake.server_port}'
        self.agent=Agent(self.config)
    def tearDown(self):
        self.fake.shutdown(); self.fake.server_close(); self.thread.join()
        super().tearDown()
    def test_learning_changes_decision(self):
        self.agent.seed()
        r=self.agent.investigate(CURRENT)['decision']
        self.assertEqual(len(r['proposed']),1)
        self.assertEqual(len(r['avoided']),1)
        self.assertFalse(r['excluded']) # staging is filtered upstream by strict tags
    def test_http_contract_and_reflect_scope(self):
        self.agent.seed(); self.agent.investigate(CURRENT)
        calls=self.fake.calls
        retain=next(p for path,p in calls if path.endswith('/memories'))
        self.assertFalse(retain['async'])
        self.assertTrue(retain['items'][0]['document_id'].startswith('AA-'))
        recall=next(p for path,p in calls if path.endswith('/recall'))
        self.assertEqual(recall['tags_match'],'all_strict')
        reflect=next(p for path,p in calls if path.endswith('/reflect'))
        ids=reflect['tag_groups'][1]['tags']
        self.assertIn('lesson:AA-demo-001',ids)
        self.assertNotIn('lesson:AA-demo-003',ids)
    def test_failure_keeps_outbox_and_retry(self):
        self.fake.fail=True
        r=self.agent.record({**EPISODES[0],'confirmed':True})
        self.assertIn('503',r['warning'])
        self.assertNotIn('DO NOT LEAK',r['warning'])
        self.assertEqual(self.agent.state()['pending'],1)
        self.fake.fail=False
        self.agent.sync()
        self.assertEqual(self.agent.state()['pending'],0)
    def test_no_silent_local_fallback(self):
        self.agent.seed(); self.fake.fail=True
        with self.assertRaises(MemoryUnavailable): self.agent.investigate(CURRENT)
    def test_unretrieved_local_record_is_not_evidence(self):
        self.agent.store.add(lesson(EPISODES[0]))
        self.assertFalse(self.agent.investigate(CURRENT)['decision']['eligible'])


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.server=create_server(Config(db=str(Path(self.tmp.name)/'http.db'),port=0))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def test_home_and_head(self):
        with urlopen(self.url) as r:
            self.assertIn(b'AfterAction',r.read())
            self.assertIn("frame-ancestors 'none'",r.headers['Content-Security-Policy'])
        with urlopen(Request(self.url,method='HEAD')) as r: self.assertEqual(r.status,200)
    def test_missing_header_and_wrong_origin(self):
        for headers in ({'Content-Type':'application/json'}, {'Content-Type':'application/json','X-AfterAction':'1','Origin':'https://evil.example'}):
            with self.assertRaises(HTTPError) as cm:
                urlopen(Request(self.url+'/api/seed',data=b'{}',headers=headers))
            self.assertEqual(cm.exception.code,403)
    def test_json_validation(self):
        req=Request(self.url+'/api/investigate',data=b'{"service": 4}',headers={'Content-Type':'application/json','X-AfterAction':'1'})
        with self.assertRaises(HTTPError) as cm: urlopen(req)
        self.assertEqual(cm.exception.code,400)
    def test_unknown_paths_and_bad_host(self):
        for path,headers,status in [('/.env',{},404),('/',{'Host':'evil.example'},403)]:
            with self.assertRaises(HTTPError) as cm: urlopen(Request(self.url+path,headers=headers))
            self.assertEqual(cm.exception.code,status)

if __name__ == '__main__': unittest.main()
