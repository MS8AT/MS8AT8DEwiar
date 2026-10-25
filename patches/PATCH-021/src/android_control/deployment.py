"""Validate public endpoint metadata and render a WireGuard guard without secrets."""
from pathlib import Path
import ipaddress
import json
import re

DEFAULT = {'bind_host': '127.0.0.1', 'certificate_hosts': ['localhost', '127.0.0.1']}


def validate_deployment(value):
    if not isinstance(value, dict) or set(value) != set(DEFAULT):
        raise ValueError('Expected bind_host and certificate_hosts')
    if value['bind_host'] not in ('127.0.0.1', '0.0.0.0'):
        raise ValueError('Use an explicit loopback or all-IPv4 bind')
    hosts = value['certificate_hosts']
    if not isinstance(hosts, list) or not 1 <= len(hosts) <= 16:
        raise ValueError('Expected 1 to 16 certificate hosts')
    for host in hosts:
        if not isinstance(host, str) or len(host) > 253:
            raise ValueError('Invalid certificate host')
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            labels = host.split('.')
            if not all(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', part) for part in labels):
                raise ValueError('Invalid DNS host')
            if re.fullmatch(r'[0-9.]+', host):
                raise ValueError('Invalid IPv4 host')
        else:
            if address.version != 4 or address.is_unspecified or address.is_multicast:
                raise ValueError('Expected a concrete IPv4 host')
    if len(set(hosts)) != len(hosts):
        raise ValueError('Repeated certificate host')
    # The local CLI and tray menu always use this address, even with WAN access enabled.
    if '127.0.0.1' not in hosts:
        raise ValueError('Certificate hosts must include 127.0.0.1 for the local CLI')
    return {'bind_host': value['bind_host'], 'certificate_hosts': list(hosts)}


def load_deployment(root):
    path = Path(root) / 'control-deployment.json'
    if not path.exists():
        return validate_deployment(DEFAULT)
    if path.stat().st_size > 4096:
        raise ValueError('Deployment metadata is too large')
    return validate_deployment(json.loads(path.read_text(encoding='utf-8')))


def render_guard(template, endpoint, port):
    address = ipaddress.ip_address(endpoint)
    if address.version != 4 or address.is_unspecified or address.is_multicast or address.is_loopback:
        raise ValueError('Expected the WireGuard server IPv4 address')
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Invalid WireGuard UDP port')
    if template.count('@WG_ENDPOINT_IPV4@') != 1 or template.count('@WG_ENDPOINT_PORT@') != 1:
        raise ValueError('Unexpected guard template')
    result = template.replace('@WG_ENDPOINT_IPV4@', str(address)).replace('@WG_ENDPOINT_PORT@', str(port))
    if '@WG_' in result:
        raise ValueError('Unresolved guard marker')
    return result
