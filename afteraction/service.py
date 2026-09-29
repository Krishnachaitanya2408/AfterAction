from .domain import incident, lesson, decide, BASELINE
from .memory import HindsightMemory, RehearsalMemory, MemoryUnavailable
from .store import Store
from .sample import CURRENT, EPISODES
import threading


class Agent:
    def __init__(self, config):
        self.config = config
        self.store = Store(config.db)
        self.memory = (HindsightMemory if config.mode == 'hindsight' else RehearsalMemory)(config, self.store)
        self.lock = threading.Lock()

    def state(self):
        rows = self.store.rows()
        return {'mode': self.config.mode, 'bank': self.config.bank if self.config.mode == 'hindsight' else None,
                'lessons': [{**r, 'synced': r['synced_target'] == self.memory.target} for r in rows],
                'traces': self.store.traces(), 'sample': CURRENT,
                'pending': sum(not r['retired'] and r['synced_target'] != self.memory.target for r in rows) if self.config.mode == 'hindsight' else 0}

    def record(self, data):
        if data.get('confirmed') is not True:
            raise ValueError('Confirm that this is a reviewed outcome before retaining it')
        row = self.store.add(lesson(data))
        warning = None
        try:
            self.memory.retain(row)
        except MemoryUnavailable as exc:
            warning = str(exc) + ' Outcome saved locally; use Retry sync.'
        return {'lesson': row, 'warning': warning}

    def seed(self):
        # Idempotent: fixed source IDs prevent duplicates on repeated button presses.
        for sample in EPISODES:
            self.store.add(lesson(sample), sample['id'])
        return self.sync()

    def sync(self):
        count, warnings = 0, []
        for row in self.store.rows():
            if row['retired'] or row['synced_target'] == self.memory.target:
                continue
            try:
                self.memory.retain(row)
                count += 1
            except MemoryUnavailable as exc:
                warnings.append(str(exc))
                break
        return {'processed': count, 'warnings': warnings}

    def investigate(self, data):
        current = incident(data)
        if type(data.get('use_memory', True)) is not bool:
            raise ValueError('use_memory must be a boolean')
        if not data.get('use_memory', True):
            return {'baseline': BASELINE, 'mode': 'baseline', 'summary': 'Memory disabled. No historical cause or fix can be inferred from these symptoms alone.',
                    'decision': decide(current, []), 'facts': [], 'warning': None}
        candidates, facts = self.memory.recall(current, self.store.rows())
        decision = decide(current, candidates)
        warning = None
        try:
            summary = self.memory.reflect(current, decision)
        except MemoryUnavailable as exc:
            summary = 'Reflection unavailable. The source-derived panel remains available.'
            warning = str(exc)
        return {'baseline': BASELINE, 'mode': self.config.mode, 'summary': summary,
                'decision': decision, 'facts': facts, 'warning': warning}
