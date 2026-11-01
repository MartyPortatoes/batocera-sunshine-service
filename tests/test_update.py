import hashlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('updater', str(ROOT / 'sunshine-update'))
spec = importlib.util.spec_from_loader(loader.name, loader)
updater = importlib.util.module_from_spec(spec)
loader.exec_module(updater)


class UpdateTests(unittest.TestCase):
    def asset(self, payload=b'verified release', name='Sunshine_2026.914.233613_x86_64.AppImage'):
        return {'name': name, 'size': len(payload),
                'digest': 'sha256:' + hashlib.sha256(payload).hexdigest(),
                'browser_download_url': 'https://github.com/LizardByte/Sunshine/releases/download/v1/' + name}

    def test_current_and_legacy_asset_names(self):
        for name in ['Sunshine_2026.914.233613_x86_64.AppImage', 'sunshine.AppImage']:
            asset = self.asset(name=name)
            self.assertEqual(updater.select_asset({'assets': [asset]}, 'x86_64'), asset)

    def test_selects_x86_and_rejects_ambiguous_or_unverified_releases(self):
        asset = self.asset()
        arm = self.asset(name='Sunshine_2026.914.233613_aarch64.AppImage')
        self.assertEqual(updater.select_asset({'assets': [arm, asset]}, 'x86_64'), asset)
        for release in [{'assets': []}, {'assets': [asset, asset]},
                        {'assets': [dict(asset, digest='')]},
                        {'assets': [dict(asset, browser_download_url='https://example.com/file')]}]:
            with self.assertRaises(ValueError): updater.select_asset(release, 'x86_64')
        with self.assertRaises(ValueError): updater.select_asset({'assets': [asset]}, 'aarch64')

    def test_stable_and_pinned_urls(self):
        self.assertTrue(updater.release_url('stable').endswith('/latest'))
        self.assertTrue(updater.release_url('2026.914.233613').endswith('/tags/v2026.914.233613'))
        with self.assertRaises(ValueError): updater.release_url('../../other')

    def test_verified_download_and_activation(self):
        payload = b'verified release'
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            target = updater.download_verified(self.asset(payload), directory, lambda _: io.BytesIO(payload))
            self.assertEqual(target.read_bytes(), payload)
            self.assertTrue(target.stat().st_mode & 0o111)
            link = directory / 'sunshine-service-current'
            updater.activate(target, link)
            self.assertEqual(link.resolve(), target.resolve())

    def test_failure_preserves_active_release_and_removes_partial_file(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            old = directory / 'known-good.AppImage'
            old.write_bytes(b'old')
            link = directory / 'sunshine-service-current'
            updater.activate(old, link)
            with self.assertRaises(ValueError):
                updater.download_verified(self.asset(), directory, lambda _: io.BytesIO(b'corrupted'))
            self.assertEqual(link.resolve(), old.resolve())
            self.assertEqual(old.read_bytes(), b'old')
            self.assertEqual(list(directory.glob('.sunshine-download-*')), [])
            def interrupted(_): raise OSError('network unavailable')
            with self.assertRaises(OSError): updater.download_verified(self.asset(), directory, interrupted)
            self.assertEqual(list(directory.glob('.sunshine-download-*')), [])

    def test_cached_verified_release_needs_no_download(self):
        payload = b'verified release'
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            target = directory / self.asset(payload)['name']
            target.write_bytes(payload)
            def offline(_): raise AssertionError('unexpected network access')
            self.assertEqual(updater.download_verified(self.asset(payload), directory, offline), target)
            self.assertTrue(target.stat().st_mode & 0o111)

    def test_check_is_read_only_and_stable_rejects_prereleases(self):
        release = {'tag_name': 'v2026.914.233613', 'assets': [self.asset()], 'prerelease': False}
        with tempfile.TemporaryDirectory() as temp, patch.dict('os.environ', SUNSHINE_SERVICE_ROOT=temp):
            with patch.object(updater.platform, 'machine', return_value='x86_64'):
                with patch.object(updater, 'request', return_value=io.BytesIO(json.dumps(release).encode())):
                    self.assertEqual(updater.main(['--check']), 0)
                self.assertEqual(list(Path(temp).iterdir()), [])
                release['prerelease'] = True
                with patch.object(updater, 'request', return_value=io.BytesIO(json.dumps(release).encode())):
                    with self.assertRaises(ValueError): updater.main(['--check'])


if __name__ == '__main__': unittest.main()
