import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4


class Store:
    def __init__(self, path):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS lessons (
              id TEXT PRIMARY KEY, payload TEXT NOT NULL, retired INTEGER NOT NULL DEFAULT 0,
              synced_target TEXT, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS traces (
              id INTEGER PRIMARY KEY AUTOINCREMENT, operation TEXT, status TEXT,
              detail TEXT, elapsed_ms INTEGER, created_at TEXT);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def rows(self):
        with self.connect() as db:
            return [{**json.loads(r['payload']), 'id': r['id'], 'retired': bool(r['retired']),
                     'synced_target': r['synced_target']} for r in db.execute('SELECT * FROM lessons ORDER BY created_at DESC, id')]

    def add(self, payload, row_id=None):
        row_id = row_id or 'AA-' + uuid4().hex[:12]
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO lessons(id,payload,created_at) VALUES(?,?,?)',
                       (row_id, json.dumps(payload), datetime.now(timezone.utc).isoformat()))
        return next(r for r in self.rows() if r['id'] == row_id)

    def mark_synced(self, row_id, target):
        with self.connect() as db:
            db.execute('UPDATE lessons SET synced_target=? WHERE id=?', (target, row_id))

    def retire(self, row_id):
        with self.connect() as db:
            cur = db.execute('UPDATE lessons SET retired=1 WHERE id=?', (row_id,))
            if cur.rowcount != 1:
                raise ValueError('Unknown lesson ID')

    def trace(self, operation, status, detail, elapsed_ms=0):
        with self.connect() as db:
            db.execute('INSERT INTO traces(operation,status,detail,elapsed_ms,created_at) VALUES(?,?,?,?,?)',
                       (operation, status, detail, elapsed_ms, datetime.now(timezone.utc).isoformat()))
            db.execute('DELETE FROM traces WHERE id NOT IN (SELECT id FROM traces ORDER BY id DESC LIMIT 200)')

    def traces(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM traces ORDER BY id DESC LIMIT 30')]
