"""Fictional closed incidents. No actual employer or customer data."""
CURRENT = {'service': 'payments-api', 'environment': 'production', 'architecture': 'direct-postgres',
           'symptom': 'Checkout timeouts during promotion. Database connections saturated, workers retrying, p95 latency 4200ms.'}
EPISODES = [
 {'id':'AA-demo-001', **CURRENT, 'action':'Restart all payment workers', 'outcome':'failed',
  'reason':'In this synthetic incident a simultaneous restart triggered a reconnect surge. Error rate increased from 8% to 19%. No causal claim beyond this recorded scenario.',
  'observed_at':'2026-09-01T10:30:00+00:00'},
 {'id':'AA-demo-002', **CURRENT, 'action':'Cap worker concurrency after checking queue age', 'outcome':'helped',
  'reason':'The operator reduced concurrency from 80 to 20 after checking queue age. Connection pressure fell and p95 returned below 600ms. These are fictional scenario values, not measured product results.',
  'observed_at':'2026-09-01T10:45:00+00:00'},
 {'id':'AA-demo-003', **CURRENT, 'environment':'staging', 'action':'Restart all payment workers', 'outcome':'helped',
  'reason':'A restart cleared stale connections in low-traffic staging. This result must not be generalized to production.',
  'observed_at':'2026-08-28T11:00:00+00:00'},
]
