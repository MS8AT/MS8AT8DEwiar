"""Small durable queue shared by the VM runner and the authenticated controller."""
from pathlib import Path
import json
import os
import re
import tempfile

COMMANDS = {'vpn_up': 'up', 'vpn_down': 'down', 'vpn_status': 'status'}


def write_result(request, value):
    request = Path(request)
    fd, name = tempfile.mkstemp(prefix=request.stem + '.', suffix='.tmp', dir=request.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(dict(value, id=request.stem), stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, request.with_suffix('.result'))
    finally:
        if os.path.exists(name):
            os.unlink(name)


def pending_requests(directory):
    """Bad requests get a failure result; they cannot stop or starve the VM."""
    result = []
    for path in Path(directory).glob('*.json'):
        if not re.fullmatch(r'[a-f0-9]{32}', path.stem) or path.with_suffix('.result').exists():
            continue
        try:
            if path.stat().st_size > 4096:
                raise ValueError('request too large')
            entry = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(entry, dict) or entry.get('action') not in COMMANDS:
                raise ValueError('unsupported action')
            stamp = entry.get('created_ns', path.stat().st_mtime_ns)
            if type(stamp) is not int or stamp < 0:
                raise ValueError('invalid timestamp')
            result.append((stamp, path.name, path, COMMANDS[entry['action']]))
        except (ValueError, TypeError, OSError, RecursionError):
            write_result(path, {'ok': False, 'error': 'INVALID_REQUEST', 'output': ''})
    result.sort(key=lambda item: (item[0], item[1]))
    return [(path, command) for _, _, path, command in result]
