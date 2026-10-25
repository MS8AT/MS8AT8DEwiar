"""Offline queue/API/CLI regression tests. No real credentials, sockets or VM commands."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase, main, mock
import io
import json
import os
import urllib.error

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/android_control'))
import control
import control_cli as cli
import command_queue


class QueueTests(TestCase):
    def test_request_becomes_visible_only_after_complete_json(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / ('a' * 32 + '.json')
            real_replace = os.replace

            def inspect_publication(source, destination):
                self.assertFalse(target.exists())
                self.assertEqual(list(target.parent.glob('*.json')), [])
                self.assertEqual(json.loads(Path(source).read_text()), {'action': 'vpn_up', 'created_ns': 123})
                self.assertEqual(Path(source).parent, target.parent)
                real_replace(source, destination)

            with mock.patch.object(control.os, 'replace', side_effect=inspect_publication) as publish:
                control.publish_json(target, {'action': 'vpn_up', 'created_ns': 123})
            publish.assert_called_once()
            self.assertEqual(json.loads(target.read_text())['action'], 'vpn_up')
            self.assertEqual(list(target.parent.iterdir()), [target])

    def test_failed_publication_leaves_no_partial_request_or_temp_file(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / ('a' * 32 + '.json')
            with mock.patch.object(control.os, 'replace', side_effect=OSError('synthetic failure')):
                with self.assertRaises(OSError):
                    control.publish_json(target, {'action': 'vpn_up', 'created_ns': 123})
            self.assertEqual(list(target.parent.iterdir()), [])

    def test_submission_order_survives_reversed_uuids_and_clock_rollback(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)), \
                mock.patch.object(control, 'audit'), mock.patch.object(control, 'LAST_REQUEST_NS', 0), \
                mock.patch.object(control.time, 'time_ns', side_effect=[1000, 900, 1000]), \
                mock.patch.object(control.uuid, 'uuid4', side_effect=[SimpleNamespace(hex=c * 32) for c in 'cba']):
            replies = [control.action({'action': 'vpn', 'enabled': False}),
                       control.action({'action': 'vpn', 'enabled': True}),
                       control.action({'action': 'vpn-status'})]
            entries = [json.loads(path.read_text()) for path in (Path(directory) / 'requests').glob('*.json')]
            ordered = sorted(entries, key=lambda value: value['created_ns'])
            self.assertEqual([value['action'] for value in ordered], ['vpn_down', 'vpn_up', 'vpn_status'])
            self.assertEqual([value['created_ns'] for value in ordered], [1000, 1001, 1002])
            self.assertEqual([reply['request_id'] for reply in replies], [c * 32 for c in 'cba'])
            self.assertTrue(all(reply['accepted'] for reply in replies))
            self.assertEqual([command for _, command in command_queue.pending_requests(Path(directory) / 'requests')],
                             ['down', 'up', 'status'])

    def test_concurrent_submissions_have_unique_monotonic_sequence(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)), \
                mock.patch.object(control, 'audit'), mock.patch.object(control, 'LAST_REQUEST_NS', 0), \
                mock.patch.object(control.time, 'time_ns', return_value=1000):
            with ThreadPoolExecutor(max_workers=6) as pool:
                replies = list(pool.map(lambda _: control.action({'action': 'vpn-status'}), range(24)))
            entries = [json.loads(path.read_text()) for path in (Path(directory) / 'requests').glob('*.json')]
            self.assertEqual(len({reply['request_id'] for reply in replies}), 24)
            self.assertEqual(sorted(value['created_ns'] for value in entries), list(range(1000, 1024)))

    def test_invalid_action_does_not_create_queue(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)):
            with self.assertRaises(ValueError):
                control.action({'action': 'vpn', 'enabled': 'false'})
            with self.assertRaises(ValueError):
                control.action({'action': 'host_shell', 'command': 'ignored'})
            self.assertEqual(list(Path(directory).iterdir()), [])


class QueueReaderTests(TestCase):
    def request(self, directory, ident, value):
        path = Path(directory) / (ident * 32 + '.json')
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def test_reader_skips_done_and_temporary_entries_and_orders_fifo(self):
        with TemporaryDirectory() as directory:
            early = self.request(directory, 'c', {'action': 'vpn_down', 'created_ns': 10})
            late = self.request(directory, 'a', {'action': 'vpn_up', 'created_ns': 20})
            done = self.request(directory, 'b', {'action': 'vpn_status', 'created_ns': 1})
            command_queue.write_result(done, {'ok': True})
            (Path(directory) / '.upload.tmp').write_text('{')
            (Path(directory) / 'invalid-name.json').write_text('{')
            self.assertEqual(command_queue.pending_requests(directory), [(early, 'down'), (late, 'up')])

    def test_reader_uses_mtime_for_legacy_requests(self):
        with TemporaryDirectory() as directory:
            early = self.request(directory, 'b', {'action': 'vpn_down'})
            late = self.request(directory, 'a', {'action': 'vpn_up'})
            os.utime(early, ns=(1_000_000_000, 1_000_000_000))
            os.utime(late, ns=(2_000_000_000, 2_000_000_000))
            self.assertEqual(command_queue.pending_requests(directory), [(early, 'down'), (late, 'up')])

    def test_adversarial_entries_fail_individually_without_starving_valid_work(self):
        documents = ['{', '[]', 'null', '{"action":[]}', '{"action":"host_shell"}',
                     '{"action":"vpn_up","created_ns":true}',
                     '{"action":"vpn_up","created_ns":-1}',
                     '{"action":"vpn_up","created_ns":"1"}',
                     ' ' * 4097, '[' * 1500 + '0' + ']' * 1500]
        with TemporaryDirectory() as directory:
            bad = []
            for number, document in enumerate(documents):
                path = Path(directory) / (f'{number:032x}' + '.json')
                path.write_text(document, encoding='utf-8')
                bad.append(path)
            valid = self.request(directory, 'f', {'action': 'vpn_status', 'created_ns': 42})
            self.assertEqual(command_queue.pending_requests(directory), [(valid, 'status')])
            for path in bad:
                value = json.loads(path.with_suffix('.result').read_text())
                self.assertEqual(value['id'], path.stem)
                self.assertFalse(value['ok'])
                self.assertEqual(value['error'], 'INVALID_REQUEST')
            # Poisoned entries are complete, so another pass still reaches useful work.
            self.assertEqual(command_queue.pending_requests(directory), [(valid, 'status')])

    def test_result_is_atomically_published_with_request_identity(self):
        with TemporaryDirectory() as directory:
            request = self.request(directory, 'a', {'action': 'vpn_status', 'created_ns': 1})
            final = request.with_suffix('.result')
            real_replace = os.replace

            def inspect_publication(source, destination):
                self.assertFalse(final.exists())
                value = json.loads(Path(source).read_text())
                self.assertEqual(value, {'ok': True, 'output': 'UP', 'id': request.stem})
                self.assertEqual(Path(source).parent, final.parent)
                real_replace(source, destination)

            with mock.patch.object(command_queue.os, 'replace', side_effect=inspect_publication):
                command_queue.write_result(request, {'ok': True, 'output': 'UP', 'id': 'ignored-id'})
            self.assertTrue(json.loads(final.read_text())['ok'])
            self.assertEqual(list(Path(directory).glob('*.tmp')), [])

    def test_result_publish_failure_does_not_leave_partial_result(self):
        with TemporaryDirectory() as directory:
            request = self.request(directory, 'a', {'action': 'vpn_status', 'created_ns': 1})
            with mock.patch.object(command_queue.os, 'replace', side_effect=OSError('synthetic failure')):
                with self.assertRaises(OSError):
                    command_queue.write_result(request, {'ok': True})
            self.assertFalse(request.with_suffix('.result').exists())
            self.assertEqual(list(Path(directory).glob('*.tmp')), [])


class ApiTests(TestCase):
    def handler(self):
        handler = object.__new__(control.HTTP)
        handler.server = SimpleNamespace(token='synthetic-test-token')
        handler.reply = mock.Mock()
        return handler

    def test_non_ascii_bearer_denied_without_handler_exception(self):
        handler = self.handler()
        handler.headers = {'Authorization': 'Bearer \u00ff'}
        self.assertFalse(handler.authorized())
        handler.reply.assert_called_once_with(401, {'error': 'authentication required'})

    def test_valid_bearer_is_accepted(self):
        handler = self.handler()
        handler.headers = {'Authorization': 'Bearer synthetic-test-token'}
        self.assertTrue(handler.authorized())
        handler.reply.assert_not_called()

    def test_corrupt_result_is_controlled_503(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)):
            queue = Path(directory) / 'requests'
            queue.mkdir()
            ident = 'a' * 32
            (queue / (ident + '.result')).write_text('{')
            handler = self.handler()
            handler.headers = {'Authorization': 'Bearer synthetic-test-token'}
            handler.path = '/v1/requests/' + ident
            handler.do_GET()
            handler.reply.assert_called_once_with(503, {'error': 'request result unavailable', 'request_id': ident})


class CliTests(TestCase):
    ident = 'a' * 32

    def args(self, action='vpn-status'):
        return SimpleNamespace(action=action, host='127.0.0.1', size=None, enabled=None)

    def execute(self, replies, action='vpn-status'):
        with mock.patch.object(cli, 'request_json', side_effect=replies), mock.patch.object(cli.time, 'sleep'):
            return cli.execute(self.args(action), 'synthetic-test-token', object())

    def test_completed_request_returns_success(self):
        result, code = self.execute([{'accepted': True, 'request_id': self.ident},
                                     {'pending': True}, {'ok': True, 'id': self.ident, 'output': 'ready'}])
        self.assertEqual(code, 0)
        self.assertTrue(result['ok'])

    def test_failed_request_returns_nonzero(self):
        result, code = self.execute([{'accepted': True, 'request_id': self.ident},
                                     {'ok': False, 'id': self.ident, 'output': 'failed'}])
        self.assertEqual(code, 1)
        self.assertFalse(result['ok'])

    def test_pending_deadline_returns_nonzero_with_request_id(self):
        current = [0.0]

        def sleep(seconds):
            current[0] += seconds

        with mock.patch.object(cli, 'request_json', side_effect=[{'accepted': True, 'request_id': self.ident}] + [{'pending': True}] * 40), \
                mock.patch.object(cli.time, 'monotonic', side_effect=lambda: current[0]), \
                mock.patch.object(cli.time, 'sleep', side_effect=sleep):
            result, code = cli.execute(self.args(), 'synthetic-test-token', object())
        self.assertEqual(code, 3)
        self.assertEqual(result['error'], 'request_timeout')
        self.assertEqual(result['request_id'], self.ident)

    def test_http_error_is_nonzero_without_server_body_or_token(self):
        failure = urllib.error.HTTPError('https://invalid', 401, 'synthetic-sensitive-details', {}, None)
        result, code = self.execute([failure])
        self.assertEqual((code, result), (1, {'ok': False, 'error': 'http_error', 'status': 401}))

    def test_transport_error_retains_accepted_request_id(self):
        result, code = self.execute([{'accepted': True, 'request_id': self.ident},
                                     urllib.error.URLError('synthetic-sensitive-details')])
        self.assertEqual(code, 1)
        self.assertEqual(result, {'ok': False, 'error': 'connection_failed', 'request_id': self.ident})

    def test_malformed_accepted_reply_does_not_poll_arbitrary_path(self):
        with mock.patch.object(cli, 'request_json', return_value={'accepted': True, 'request_id': '../credentials'}) as call:
            result, code = cli.execute(self.args(), 'synthetic-test-token', object())
        call.assert_called_once()
        self.assertEqual(code, 1)
        self.assertEqual(result, {'ok': False, 'error': 'invalid_response'})

    def test_action_result_requires_boolean_ok(self):
        result, code = self.execute([{'accepted': True, 'request_id': self.ident}, {'ok': 'false'}])
        self.assertEqual(code, 1)
        self.assertEqual(result['error'], 'invalid_response')

    def test_direct_action_result_requires_boolean_ok(self):
        result, code = self.execute([{'ok': 'false'}], action='stop')
        self.assertEqual(code, 1)
        self.assertEqual(result['error'], 'invalid_response')

    def test_status_reply_does_not_require_action_ok(self):
        result, code = self.execute([{'android': {'phase': 'ready'}}], action='status')
        self.assertEqual(code, 0)
        self.assertEqual(result['android']['phase'], 'ready')

    def test_main_returns_failure_and_prints_sanitized_json(self):
        output = io.StringIO()
        with mock.patch.object(cli, 'load_credentials', return_value=('synthetic-test-token', object())), \
                mock.patch.object(cli, 'request_json', side_effect=OSError('synthetic-sensitive-details')), redirect_stdout(output):
            code = cli.main(['status'])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue()), {'ok': False, 'error': 'connection_failed'})


class LogTests(TestCase):
    def test_audit_tail_is_bounded_and_drops_unapproved_fields(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)):
            logs = Path(directory) / 'logs'
            logs.mkdir()
            rows = [{'event': 'action', 'action': 'status', 'secret': 'synthetic-secret', 'at': str(i)} for i in range(300)]
            (logs / 'control.jsonl').write_text('\n'.join(json.dumps(row) for row in rows))
            output = control.recent_logs()
            self.assertEqual(len(output), 100)
            self.assertEqual(output[0]['at'], '200')
            self.assertTrue(all('secret' not in item for item in output))

    def test_audit_reader_skips_corrupt_records(self):
        with TemporaryDirectory() as directory, mock.patch.object(control, 'ROOT', Path(directory)):
            logs = Path(directory) / 'logs'
            logs.mkdir()
            (logs / 'control.jsonl').write_text('{unfinished\n[1,2]\n{"event":"control_started"}\n')
            self.assertEqual(control.recent_logs(), [{'event': 'control_started'}])


if __name__ == '__main__':
    main(verbosity=2)
