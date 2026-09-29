from dataclasses import dataclass
from pathlib import Path
import os
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent


def load_env(path=None):
    """Small .env reader; process environment takes precedence. No shell evaluation."""
    path = Path(path or ROOT / '.env')
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('\"\''))


@dataclass
class Config:
    mode: str = 'rehearsal'
    db: str = str(ROOT / 'data' / 'afteraction.db')
    url: str = 'https://api.hindsight.vectorize.io'
    key: str = ''
    bank: str = 'afteraction-demo'
    timeout: float = 45
    host: str = '127.0.0.1'
    port: int = 8000

    @classmethod
    def from_env(cls):
        load_env()
        c = cls(mode=os.getenv('MEMORY_MODE', 'rehearsal'),
                db=os.getenv('DATABASE_PATH', str(ROOT / 'data' / 'afteraction.db')),
                url=os.getenv('HINDSIGHT_BASE_URL', 'https://api.hindsight.vectorize.io').rstrip('/'),
                key=os.getenv('HINDSIGHT_API_KEY', ''),
                bank=os.getenv('HINDSIGHT_BANK_ID', 'afteraction-demo'),
                timeout=float(os.getenv('HINDSIGHT_TIMEOUT', '45')),
                host=os.getenv('HOST', '127.0.0.1'), port=int(os.getenv('PORT', '8000')))
        if c.mode not in ('rehearsal', 'hindsight'):
            raise ValueError('MEMORY_MODE must be rehearsal or hindsight')
        parsed = urlparse(c.url)
        if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1', 'hindsight')):
            raise ValueError('Use HTTPS for remote Hindsight, or HTTP for a local Hindsight instance')
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('HINDSIGHT_BASE_URL must not include credentials, query, or fragment')
        if not c.bank or len(c.bank) > 100:
            raise ValueError('Set a HINDSIGHT_BANK_ID of 1–100 characters')
        return c
