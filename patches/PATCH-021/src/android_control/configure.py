"""Create non-secret deployment files in a NEW directory; no installation or network."""
from pathlib import Path
import argparse
import hashlib
import json
from deployment import render_guard, validate_deployment


def stage(output, endpoint, port, bind_host, hosts):
    config = validate_deployment({'bind_host': bind_host, 'certificate_hosts': hosts})
    template = Path(__file__).with_name('guest-wg.sh.in').read_text(encoding='utf-8')
    guard = render_guard(template, endpoint, port).encode('utf-8')
    output = Path(output)
    output.mkdir(parents=False, exist_ok=False)
    (output / 'control-deployment.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    (output / 'guest-wg.sh').write_bytes(guard)
    receipt = {'schema': 1, 'installed': False, 'network_calls': 0,
               'files': {name: hashlib.sha256((output / name).read_bytes()).hexdigest()
                         for name in ('control-deployment.json', 'guest-wg.sh')}}
    (output / 'SHA256.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--endpoint-ipv4', required=True)
    parser.add_argument('--endpoint-port', type=int, required=True)
    parser.add_argument('--bind-host', choices=['127.0.0.1', '0.0.0.0'], default='127.0.0.1')
    parser.add_argument('--certificate-host', action='append', dest='hosts')
    args = parser.parse_args()
    try:
        result = stage(args.output, args.endpoint_ipv4, args.endpoint_port, args.bind_host,
                       args.hosts or ['localhost', '127.0.0.1'])
    except (ValueError, OSError) as error:
        parser.exit(1, 'REFUSED: ' + str(error) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
