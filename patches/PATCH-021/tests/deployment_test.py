"""Synthetic deployment tests; no sockets, VM, secrets or real user files."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import sys
import unittest

SRC = Path(__file__).resolve().parents[1] / 'src/android_control'
sys.path.insert(0, str(SRC))
from deployment import DEFAULT, load_deployment, render_guard, validate_deployment
from configure import stage


class DeploymentTests(unittest.TestCase):
    def test_default_only_listens_locally_and_returns_independent_copy(self):
        with TemporaryDirectory() as directory:
            value = load_deployment(directory)
            self.assertEqual(value['bind_host'], '127.0.0.1')
            value['certificate_hosts'].append('fixture.invalid')
            self.assertEqual(load_deployment(directory), DEFAULT)

    def test_explicit_external_listener(self):
        value = {'bind_host': '0.0.0.0', 'certificate_hosts': ['localhost', '127.0.0.1', 'test.example', '192.0.2.10']}
        self.assertEqual(validate_deployment(value), value)

    def test_remote_only_certificate_cannot_break_local_menu_and_cli(self):
        for hosts in [['localhost'], ['android.example'], ['192.0.2.10']]:
            with self.subTest(hosts=hosts), self.assertRaises(ValueError):
                validate_deployment({'bind_host': '0.0.0.0', 'certificate_hosts': hosts})

    def test_unknown_keys_wrong_types_and_unsafe_hosts_are_rejected(self):
        values = [[], {}, dict(DEFAULT, token='synthetic'), dict(DEFAULT, bind_host='::'),
                  dict(DEFAULT, certificate_hosts=[]), dict(DEFAULT, certificate_hosts='host')]
        for host in ['-oProxyCommand=x', 'a/b', '*', 'a\nb', '999.999.1.1', '::1', '0.0.0.0', '224.0.0.1', 'a..b', 'x' * 64]:
            values.append(dict(DEFAULT, certificate_hosts=[host]))
        values += [dict(DEFAULT, certificate_hosts=['a'] * 2)]
        for value in values:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_deployment(value)

    def test_invalid_local_file_does_not_fall_back_to_defaults(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'control-deployment.json'
            for data in ['{', '[]', ' ' * 4097]:
                path.write_text(data, encoding='utf-8')
                with self.assertRaises(ValueError):
                    load_deployment(directory)

    def test_guard_keeps_atomic_rules_and_only_substitutes_endpoint(self):
        template = (SRC / 'guest-wg.sh.in').read_text(encoding='utf-8')
        rendered = render_guard(template, '192.0.2.7', 51820)
        self.assertIn('-d 192.0.2.7 -p udp --dport 51820', rendered)
        self.assertIn("iptables-restore --noflush <<'RULES'", rendered)
        self.assertIn('\nCOMMIT\n', rendered)
        self.assertNotIn('@WG_', rendered)
        self.assertEqual(rendered.replace('192.0.2.7', '@WG_ENDPOINT_IPV4@').replace('--dport 51820', '--dport @WG_ENDPOINT_PORT@'), template)

    def test_guard_rejects_shell_injection_and_bad_port(self):
        template = (SRC / 'guest-wg.sh.in').read_text(encoding='utf-8')
        for endpoint, port in [('192.0.2.7;id', 443), ('example.com', 443), ('127.0.0.1', 443),
                               ('0.0.0.0', 443), ('::1', 443), ('192.0.2.7', True),
                               ('192.0.2.7', 0), ('192.0.2.7', 65536)]:
            with self.subTest(endpoint=endpoint, port=port), self.assertRaises(ValueError):
                render_guard(template, endpoint, port)

    def test_broken_guard_template_is_rejected(self):
        for template in ['', '@WG_ENDPOINT_IPV4@', '@WG_ENDPOINT_IPV4@ @WG_ENDPOINT_IPV4@ @WG_ENDPOINT_PORT@',
                         '@WG_ENDPOINT_IPV4@ @WG_ENDPOINT_PORT@ @WG_BAD@']:
            with self.assertRaises(ValueError):
                render_guard(template, '192.0.2.7', 443)

    def test_staging_hashes_match_and_existing_output_is_preserved(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / 'new'
            receipt = stage(target, '192.0.2.7', 443, '127.0.0.1', ['127.0.0.1'])
            self.assertFalse(receipt['installed'])
            self.assertEqual(receipt['network_calls'], 0)
            for name, sha in receipt['files'].items():
                self.assertEqual(hashlib.sha256((target / name).read_bytes()).hexdigest(), sha)
            before = {p.name: p.read_bytes() for p in target.iterdir()}
            with self.assertRaises(FileExistsError):
                stage(target, '192.0.2.9', 443, '0.0.0.0', ['127.0.0.1', 'test.example'])
            self.assertEqual(before, {p.name: p.read_bytes() for p in target.iterdir()})

    def test_invalid_input_creates_nothing(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / 'new'
            with self.assertRaises(ValueError):
                stage(target, 'bad', 443, '127.0.0.1', ['localhost'])
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
