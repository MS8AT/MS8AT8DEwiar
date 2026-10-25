"""CLI for the authenticated local Android controller. Never prints its token."""
from pathlib import Path
import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
POLL_SECONDS = 30


def load_credentials():
    token = (ROOT / 'credentials/api-token.txt').read_text().strip()
    context = ssl.create_default_context(cafile=str(ROOT / 'credentials/api-cert.pem'))
    return token, context


def request_json(url, token, context, body=None, timeout=30):
    request = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, context=context, timeout=timeout) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise ValueError('Expected JSON object')
    return value


def execute(args, token, context):
    body = {'action': args.action}
    if args.size:
        body['size'] = args.size
    if args.enabled:
        body['enabled'] = args.enabled == 'true'
    base = f'https://{args.host}:18769/v1/'
    read_only = args.action in ('status', 'capabilities', 'logs')
    request_id = None
    try:
        result = request_json(base + (args.action if read_only else 'action'), token, context,
                              None if read_only else body)
        if result.get('accepted'):
            candidate = result.get('request_id')
            if not isinstance(candidate, str) or not re.fullmatch(r'[a-f0-9]{32}', candidate):
                raise ValueError('Invalid request id')
            request_id = candidate
            deadline = time.monotonic() + POLL_SECONDS
            while time.monotonic() < deadline:
                time.sleep(min(1, max(0, deadline - time.monotonic())))
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                result = request_json(base + 'requests/' + request_id, token, context,
                                      timeout=min(5, remaining))
                if not result.get('pending'):
                    if type(result.get('ok')) is not bool:
                        raise ValueError('Invalid action result')
                    return result, 0 if result['ok'] else 1
            return {'ok': False, 'error': 'request_timeout', 'request_id': request_id,
                    'message': 'The request is still pending. Check its status before retrying.'}, 3
        if not read_only and type(result.get('ok')) is not bool:
            raise ValueError('Invalid action result')
        return result, 1 if result.get('ok') is False or 'error' in result else 0
    except urllib.error.HTTPError as error:
        result = {'ok': False, 'error': 'http_error', 'status': error.code}
    except (urllib.error.URLError, OSError, TimeoutError):
        result = {'ok': False, 'error': 'connection_failed'}
    except (ValueError, TypeError):
        result = {'ok': False, 'error': 'invalid_response'}
    if request_id:
        result['request_id'] = request_id
    return result, 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'capabilities', 'logs', 'start', 'stop', 'open', 'screen', 'lock', 'autostart', 'vpn', 'vpn-status'])
    parser.add_argument('--size', choices=['800x500', '960x600', '1280x800'])
    parser.add_argument('--enabled', choices=['true', 'false'])
    parser.add_argument('--host', default='127.0.0.1')
    args = parser.parse_args(argv)
    if not args.host or any(char in args.host for char in '/@:#?'):
        parser.error('Expected hostname or IPv4 address')
    try:
        token, context = load_credentials()
    except (OSError, ValueError):
        result, code = {'ok': False, 'error': 'local_credentials_unavailable'}, 1
    else:
        result, code = execute(args, token, context)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
