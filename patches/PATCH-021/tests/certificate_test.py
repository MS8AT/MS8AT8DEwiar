"""Certificate metadata tests on synthetic temporary deployment, without creating keys."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/android_control'))
import control


class CertificateTests(TestCase):
    def test_san_uses_only_explicit_local_metadata(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)):
            data = {'bind_host': '0.0.0.0', 'certificate_hosts': ['localhost', 'test.example', '127.0.0.1', '192.0.2.10']}
            (Path(directory) / 'control-deployment.json').write_text(json.dumps(data), encoding='utf-8')
            result = control.certificate_names()
            self.assertEqual([str(item.value) for item in result], data['certificate_hosts'])
            self.assertIsInstance(result[-1], control.x509.IPAddress)
            self.assertIsInstance(result[1], control.x509.DNSName)
            self.assertEqual({path.name for path in Path(directory).iterdir()}, {'control-deployment.json'})

    def test_default_san_contains_no_deployment_hosts(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)):
            self.assertEqual([str(item.value) for item in control.certificate_names()], ['localhost', '127.0.0.1'])

    def test_invalid_config_stops_certificate_preparation(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)):
            (Path(directory) / 'control-deployment.json').write_text('{"bind_host":"0.0.0.0"}', encoding='utf-8')
            with self.assertRaises(ValueError):
                control.certificate_names()


if __name__ == '__main__':
    main(verbosity=2)
