"""Authenticated HTTPS control and SSH-to-Android bridge. No host shell over SSH."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))
import asyncio
import ctypes
import hashlib
import http.server
import ipaddress
import json
import os
import secrets
import ssl
import subprocess
import tempfile
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
import asyncssh
from deployment import load_deployment
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

CREDENTIALS = ROOT / 'credentials'
ADB = ROOT / 'platform-tools/adb.exe'
API_PORT = 18769
SSH_PORT = 2222
SIZES = ('800x500', '960x600', '1280x800')
LOG_LOCK = threading.Lock()
ACTION_LOCK = threading.Lock()
LAST_REQUEST_NS = 0


def audit(event, **fields):
    # Do not record tokens, keys, shell commands, request bodies or command output.
    with LOG_LOCK, (ROOT / 'logs/control.jsonl').open('a', encoding='utf-8') as file:
        file.write(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(), event=event, **fields)) + '\n')


def load_state():
    value = json.loads((ROOT / 'state.json').read_text(encoding='utf-8'))
    age = time.time() - datetime.fromisoformat(value['updated_at']).timestamp()
    return {key: value.get(key) for key in ('status', 'phase', 'health', 'vm_running',
        'android_boot_completed', 'app_process_alive', 'ram_mib', 'updated_at',
        'vpn_boot_setup', 'vpn_interface_up')} | {'stale': age > 90}


def recent_logs():
    path = ROOT / 'logs/control.jsonl'
    if not path.exists():
        return []
    with path.open('rb') as file:
        file.seek(0, 2)
        offset = max(0, file.tell() - 65536)
        file.seek(offset)
        if offset:
            file.readline()
        lines = file.read(65536).splitlines()[-100:]
    allowed = {'at', 'event', 'action', 'request', 'outcome', 'exit', 'seconds', 'api_port', 'ssh_port', 'error'}
    result = []
    for line in lines:
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                result.append({key: value[key] for key in allowed if key in value})
        except (ValueError, RecursionError):
            continue
    return result


def serial():
    import re
    value = json.loads((ROOT / 'state.json').read_text(encoding='utf-8'))
    target = value.get('adb_serial', '')
    if value.get('phase') != 'ready' or not value.get('vm_running') or not re.fullmatch(r'127\.0\.0\.1:\d+', target):
        raise ValueError('Android is not ready')
    return target


def android(*args):
    result = subprocess.run([str(ADB), '-s', serial(), 'shell', *args], capture_output=True,
                            timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError('Android command failed')
    return result.stdout.decode('utf-8', errors='replace').strip()


def settings():
    path = ROOT / 'control-settings.json'
    return json.loads(path.read_text()) if path.exists() else {'size': '960x600', 'screen_lock': False}


def save_settings(value):
    path = ROOT / 'control-settings.tmp'
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    path.replace(ROOT / 'control-settings.json')


def publish_json(path, value):
    """Readers see either no file or the complete UTF-8 JSON document."""
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.stem + '-', suffix='.tmp')
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as file:
            json.dump(value, file)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def script(name):
    # Only fixed filenames from the action map reach this host command.
    run = subprocess.run(['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-File', str(ROOT / name)],
        cwd=ROOT, capture_output=True, timeout=25, creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:
        raise RuntimeError('Control script failed')


def action(data):
    global LAST_REQUEST_NS
    name = data.get('action')
    with ACTION_LOCK:
        if name in ('start', 'stop', 'open'):
            script({'start': 'Start.ps1', 'stop': 'Stop.ps1', 'open': 'Open.ps1'}[name])
        elif name == 'screen':
            size = data.get('size')
            if size not in SIZES:
                raise ValueError('Unsupported screen size')
            android('wm', 'size', size)
            save_settings(settings() | {'size': size})
            script('Window.ps1')
        elif name == 'lock':
            enabled = data.get('enabled')
            if type(enabled) is not bool:
                raise ValueError('enabled must be boolean')
            android('locksettings', 'set-disabled', 'false' if enabled else 'true')
            android('settings', 'put', 'system', 'screen_off_timeout', '600000' if enabled else '2147483647')
            android('svc', 'power', 'stayon', 'false' if enabled else 'true')
            save_settings(settings() | {'screen_lock': enabled})
        elif name == 'autostart':
            enabled = data.get('enabled')
            if type(enabled) is not bool:
                raise ValueError('enabled must be boolean')
            script('Register-Autostart.ps1' if enabled else 'Disable-Autostart.ps1')
        elif name in ('vpn', 'vpn-status'):
            enabled = data.get('enabled')
            if name == 'vpn' and type(enabled) is not bool:
                raise ValueError('enabled must be boolean')
            ident = uuid.uuid4().hex
            directory = ROOT / 'requests'
            directory.mkdir(exist_ok=True)
            operation = 'vpn_status' if name == 'vpn-status' else ('vpn_up' if enabled else 'vpn_down')
            # The reader orders by created_ns, never by the random request UUID.
            LAST_REQUEST_NS = max(time.time_ns(), LAST_REQUEST_NS + 1)
            publish_json(directory / (ident + '.json'), {'action': operation, 'created_ns': LAST_REQUEST_NS})
            if name == 'vpn':
                save_settings(settings() | {'vpn_enabled': enabled})
            audit('action_queued', action=name, request=ident)
            return {'accepted': True, 'request_id': ident}
        else:
            raise ValueError('Unknown action')
        audit('action', action=name, outcome='ok')
        return {'ok': True, 'action': name, 'settings': settings()}


def certificate_names():
    result = []
    for host in load_deployment(ROOT)['certificate_hosts']:
        try:
            result.append(x509.IPAddress(ipaddress.ip_address(host)))
        except ValueError:
            result.append(x509.DNSName(host))
    return result


def prepare_credentials():
    # The directory is created with a current-user + SYSTEM-only Windows ACL by the installer.
    if not CREDENTIALS.is_dir():
        raise RuntimeError('Protected credentials directory is missing')
    token_path = CREDENTIALS / 'api-token.txt'
    if not token_path.exists():
        token_path.write_text(secrets.token_urlsafe(32), encoding='ascii')
    if not (CREDENTIALS / 'ssh-host').exists():
        asyncssh.generate_private_key('ssh-ed25519').write_private_key(CREDENTIALS / 'ssh-host')
    if not (CREDENTIALS / 'api-cert.pem').exists():
        key = ec.generate_private_key(ec.SECP256R1())
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'MS8AT Android control')])
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
                .serial_number(x509.random_serial_number()).not_valid_before(datetime.now(timezone.utc) - timedelta(minutes=5))
                .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
                .add_extension(x509.SubjectAlternativeName(certificate_names()), False)
                .sign(key, hashes.SHA256()))
        (CREDENTIALS / 'api-key.pem').write_bytes(key.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        (CREDENTIALS / 'api-cert.pem').write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return token_path.read_text().strip()


class HTTP(http.server.BaseHTTPRequestHandler):
    server_version = 'MS8AT-Android/1'

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *args):
        pass

    def reply(self, code, value):
        raw = json.dumps(value).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        if code == 401:
            self.send_header('WWW-Authenticate', 'Bearer realm="MS8AT Android"')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def authorized(self):
        supplied = self.headers.get('Authorization', '')
        if not secrets.compare_digest(supplied.encode('utf-8'), ('Bearer ' + self.server.token).encode('utf-8')):
            self.reply(401, {'error': 'authentication required'})
            return False
        return True

    def do_GET(self):
        if not self.authorized():
            return
        if self.path == '/v1/capabilities':
            self.reply(200, {'api': 1, 'actions': ['start', 'stop', 'open', 'screen', 'lock', 'autostart', 'vpn', 'vpn-status'],
                'read': ['status', 'capabilities', 'logs'], 'sizes': list(SIZES),
                'ssh': {'port': SSH_PORT, 'user': 'android', 'scope': 'Android shell only'}})
            return
        if self.path == '/v1/logs':
            self.reply(200, {'events': recent_logs(), 'limit': 100})
            return
        if self.path.startswith('/v1/requests/'):
            import re
            ident = self.path.removeprefix('/v1/requests/')
            if not re.fullmatch('[a-f0-9]{32}', ident):
                self.reply(400, {'error': 'invalid request id'})
                return
            path = ROOT / 'requests' / (ident + '.result')
            if path.is_file():
                try:
                    value = json.loads(path.read_text(encoding='utf-8'))
                except (OSError, ValueError):
                    self.reply(503, {'error': 'request result unavailable', 'request_id': ident})
                    return
                self.reply(200, value)
            else:
                self.reply(202, {'pending': True, 'request_id': ident})
            return
        if self.path != '/v1/status':
            self.reply(404, {'error': 'not found'})
            return
        try:
            self.reply(200, {'android': load_state(), 'settings': settings(), 'ssh_port': SSH_PORT})
        except (OSError, ValueError, KeyError):
            self.reply(503, {'error': 'status unavailable'})

    def do_POST(self):
        if not self.authorized():
            return
        if self.path != '/v1/action':
            self.reply(404, {'error': 'not found'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 2 or length > 4096 or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                raise ValueError('Expected small JSON request')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Expected JSON object')
            self.reply(200, action(data))
        except (ValueError, TypeError):
            self.reply(400, {'error': 'invalid action or parameters'})
        except (RuntimeError, OSError, subprocess.TimeoutExpired):
            self.reply(503, {'error': 'action failed; inspect local status'})


class LimitedHTTP(http.server.ThreadingHTTPServer):
    daemon_threads = True
    slots = threading.BoundedSemaphore(12)

    def process_request(self, request, address):
        if not self.slots.acquire(False):
            request.close()
            return
        try:
            super().process_request(request, address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            request.settimeout(8)
            with self.context.wrap_socket(request, server_side=True) as secure:
                self.finish_request(secure, address)
        except (OSError, ssl.SSLError):
            request.close()
        finally:
            self.slots.release()


class SSH(asyncssh.SSHServer):
    def connection_made(self, connection):
        self.connection = connection
        self.attempts = 0

    def begin_auth(self, username):
        return True

    def public_key_auth_supported(self):
        return True

    def validate_public_key(self, username, key):
        expected = asyncssh.read_public_key(CREDENTIALS / 'android_ed25519.pub')
        valid = username == 'android' and key == expected
        if not valid:
            self.attempts += 1
            if self.attempts >= 3:
                self.connection.abort()
        return valid


async def ssh_session(process):
    started = time.monotonic()
    child = None
    try:
        if process.subsystem or (process.command and len(process.command) > 16384):
            raise ValueError('Only bounded Android shell sessions are supported')
        target = serial()
        args = [str(ADB), '-s', target, 'shell', '-T']
        if process.command:
            # adb sends this to Android's shell. shell=True is never used on Windows.
            args += [process.command]
        child = await asyncio.create_subprocess_exec(*args, stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW)

        async def incoming():
            try:
                while data := await process.stdin.read(8192):
                    child.stdin.write(data)
                    await child.stdin.drain()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                child.stdin.close()

        async def outgoing(source, destination):
            while data := await source.read(8192):
                destination.write(data)
                await destination.drain()

        reader = asyncio.create_task(incoming())
        try:
            await asyncio.wait_for(asyncio.gather(outgoing(child.stdout, process.stdout),
                outgoing(child.stderr, process.stderr), child.wait()), timeout=900)
        finally:
            reader.cancel()
        process.exit(child.returncode)
        audit('ssh_session', exit=child.returncode, seconds=round(time.monotonic()-started, 2))
    except (ValueError, OSError, asyncio.TimeoutError, asyncssh.Error):
        process.stderr.write(b'Android command unavailable or timed out\n')
        process.exit(1)
        audit('ssh_session', outcome='failed')
    finally:
        if child and child.returncode is None:
            child.kill()
            await child.wait()


async def main():
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, 'Local\\MS8AT.DewiarAndroid.Control')
    if not mutex:
        raise ctypes.WinError()
    if ctypes.windll.kernel32.GetLastError() == 183:
        return
    deployment = load_deployment(ROOT)
    token = prepare_credentials()
    (ROOT / 'logs').mkdir(exist_ok=True)
    server = LimitedHTTP((deployment['bind_host'], API_PORT), HTTP)
    server.token = token
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(CREDENTIALS / 'api-cert.pem', CREDENTIALS / 'api-key.pem')
    server.context = context
    async with await asyncssh.create_server(SSH, deployment['bind_host'], SSH_PORT,
            server_host_keys=[CREDENTIALS / 'ssh-host'], process_factory=ssh_session,
            encoding=None, login_timeout=15):
        threading.Thread(target=server.serve_forever, daemon=True).start()
        audit('control_started', api_port=API_PORT, ssh_port=SSH_PORT)
        await asyncio.Future()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as error:
        try:
            audit('control_failed', error=type(error).__name__)
        except OSError:
            pass
        raise
