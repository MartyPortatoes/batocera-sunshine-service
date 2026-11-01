import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(platform.system() == 'Linux' and shutil.which('setsid') and shutil.which('flock'),
                     'Process-group tests require Linux, setsid and flock')
class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'bin').mkdir()
        fake = self.root / 'bin/sunshine-service-current'
        fake.write_text('#!/usr/bin/env python3\nimport time\nwhile True: time.sleep(0.1)\n')
        fake.chmod(0o755)
        self.pidfile = self.root / 'sunshine.pid'
        self.env = dict(os.environ, SUNSHINE_SERVICE_ROOT=str(self.root), SUNSHINE_PIDFILE=str(self.pidfile))

    def tearDown(self):
        self.call('stop', check=False)
        self.temp.cleanup()

    def call(self, action, check=True):
        return subprocess.run(['bash', str(ROOT / 'sunshine'), action], env=self.env,
                              check=check, capture_output=True, text=True, timeout=20)

    def test_offline_start_idempotence_status_and_stop(self):
        self.assertEqual(self.call('status', check=False).returncode, 1)
        self.call('start')
        first = self.pidfile.read_text()
        self.call('start')
        self.assertEqual(self.pidfile.read_text(), first)
        self.call('status')
        self.call('stop')
        self.assertEqual(self.call('status', check=False).returncode, 1)

    def test_stale_pid_does_not_kill_an_unrelated_process(self):
        other = subprocess.Popen(['sleep', '60'])
        try:
            self.pidfile.write_text(f'{other.pid} 0\n')
            self.call('stop')
            self.assertIsNone(other.poll())
        finally:
            other.terminate()
            other.wait()

    def test_restart_preserves_existing_log(self):
        (self.root / 'logs').mkdir()
        log = self.root / 'logs/sunshine.log'
        log.write_text('previous startup\n')
        self.call('start')
        old = self.pidfile.read_text()
        self.call('restart')
        self.assertNotEqual(self.pidfile.read_text(), old)
        self.assertIn('previous startup', log.read_text())


if __name__ == '__main__': unittest.main()
