"""Local-only HTTP demo server. Do not expose directly to the public internet."""
import json
import mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit
from .config import Config, ROOT
from .service import Agent
from .memory import MemoryUnavailable


class Handler(BaseHTTPRequestHandler):
    server_version = 'AfterAction/1.0'

    def send(self, status, body, content_type='application/json'):
        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def check(self, mutation=False):
        host = self.headers.get('Host', '')
        allowed = {f'localhost:{self.server.server_port}', f'127.0.0.1:{self.server.server_port}'}
        if host not in allowed:
            raise PermissionError('Localhost access only. Open http://127.0.0.1:8000 (or your configured port).')
        origin = self.headers.get('Origin')
        if origin and origin not in {'http://' + h for h in allowed}:
            raise PermissionError('Cross-origin requests are not allowed')
        if mutation and self.headers.get('X-AfterAction') != '1':
            raise PermissionError('Missing application request header')

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        try:
            self.check()
            path = urlsplit(self.path).path
            if path == '/api/state':
                return self.send(200, self.server.agent.state())
            if path == '/api/export':
                return self.send(200, {'format': 'afteraction-lessons-v1', 'lessons': self.server.agent.store.rows()})
            routes = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css'}
            if path in routes:
                file = ROOT / 'afteraction' / 'static' / routes[path]
                mime = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
                return self.send(200, file.read_bytes(), mime + '; charset=utf-8')
            self.send(404, {'error': 'Not found'})
        except PermissionError as exc:
            self.send(403, {'error': str(exc)})

    def do_POST(self):
        acquired = False
        try:
            self.check(mutation=True)
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                raise ValueError('Content-Type must be application/json')
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 40000:
                raise ValueError('Request must be between 1 and 40000 bytes')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Expected a JSON object')
            agent = self.server.agent
            acquired = agent.lock.acquire(blocking=False)
            if not acquired:
                return self.send(409, {'error': 'An operation is in progress. Wait for it to finish.'})
            path = urlsplit(self.path).path
            if path == '/api/investigate':
                result = agent.investigate(data)
            elif path == '/api/lessons':
                result = agent.record(data)
            elif path == '/api/seed':
                result = agent.seed()
            elif path == '/api/sync':
                result = agent.sync()
            elif path == '/api/retire':
                row_id = data.get('id')
                if not isinstance(row_id, str):
                    raise ValueError('id must be text')
                agent.store.retire(row_id)
                result = {'retired': row_id}
            else:
                return self.send(404, {'error': 'Not found'})
            self.send(200, result)
        except PermissionError as exc:
            self.send(403, {'error': str(exc)})
        except (ValueError, UnicodeDecodeError) as exc:
            self.send(400, {'error': str(exc)})
        except MemoryUnavailable as exc:
            self.send(502, {'error': str(exc)})
        except Exception:
            self.send(500, {'error': 'Unexpected server error. Check local configuration and database permissions.'})
        finally:
            if acquired:
                self.server.agent.lock.release()

    def log_message(self, fmt, *args):
        # Avoid logging request bodies / incident text.
        pass


def create_server(config):
    server = ThreadingHTTPServer((config.host, config.port), Handler)
    server.agent = Agent(config)
    return server


def main():
    config = Config.from_env()
    server = create_server(config)
    print(f'AfterAction | {config.mode.upper()} | http://127.0.0.1:{server.server_port}', flush=True)
    print('Local prototype. Ctrl+C to stop. Never submit rehearsal mode as Hindsight.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
