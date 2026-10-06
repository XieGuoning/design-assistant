import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import types

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cad_bridge', ROOT / 'scripts/cad_bridge.py')
cad = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cad)


class CadValidationTests(unittest.TestCase):
    def setUp(self):
        self.job = json.loads((ROOT / 'examples/cad/new-drawing.json').read_text())

    def test_example(self):
        self.assertEqual(cad.validate(self.job), self.job)

    def test_rejects_unknown_units_paths_and_code(self):
        for key, value in [('units', 'unknown'), ('source', '../original.dwg'),
                           ('source', 'C:\\original.dwg'), ('source', 'a.dwg:stream'),
                           ('operations', [{'type': 'command', 'text': '(shell "cmd")'}])]:
            job = copy.deepcopy(self.job)
            job[key] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                cad.validate(job)

    def test_rejects_nonfinite_boolean_and_degenerate_geometry(self):
        for value in [float('nan'), float('inf'), True, '5']:
            job = copy.deepcopy(self.job)
            job['operations'][0]['end'][0] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                cad.validate(job)
        self.job['operations'][0]['end'] = [0, 0, 0]
        with self.assertRaises(ValueError):
            cad.validate(self.job)

    def test_move_requires_source_and_hex_handle(self):
        self.job['operations'] = [{'type': 'move', 'handle': 'AB12', 'offset': [1, 0, 0]}]
        with self.assertRaises(ValueError):
            cad.validate(self.job)
        self.job['source'] = 'copy.dwg'
        cad.validate(self.job)
        self.job['operations'][0]['handle'] = 'AB;quit'
        with self.assertRaises(ValueError):
            cad.validate(self.job)

    def test_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'inputs').mkdir()
            outside = root / 'secret.dwg'
            outside.write_bytes(b'original')
            (root / 'inputs' / 'copy.dwg').symlink_to(outside)
            with self.assertRaises(ValueError):
                cad.source_path(root, 'copy.dwg')
            self.assertEqual(outside.read_bytes(), b'original')

    def test_units_mismatch_closes_copy_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'inputs').mkdir()
            original = root / 'inputs' / 'room.dwg'
            original.write_bytes(b'original drawing')
            self.job['source'] = 'room.dwg'
            app = MagicMock()
            app.Version = '25.2'
            doc = app.Documents.Open.return_value
            doc.GetVariable.return_value = 0
            client = types.ModuleType('win32com.client')
            client.DispatchEx = MagicMock(return_value=app)
            win32 = types.ModuleType('win32com')
            win32.client = client
            pythoncom = MagicMock()
            with patch.object(cad.sys, 'platform', 'win32'), patch.dict(
                cad.sys.modules, {'pythoncom': pythoncom, 'win32com': win32, 'win32com.client': client}
            ), self.assertRaises(ValueError):
                cad.execute(self.job, root)
            opened = Path(app.Documents.Open.call_args.args[0])
            self.assertNotEqual(opened, original)
            self.assertEqual(original.read_bytes(), b'original drawing')
            doc.Close.assert_called_once_with(False)
            doc.Save.assert_not_called()
            self.assertTrue((opened.parent / 'FAILED.txt').exists())
            self.assertFalse((opened.parent / 'result.json').exists())

    def test_no_execution_on_linux(self):
        with patch.object(cad.sys, 'platform', 'linux'), self.assertRaises(RuntimeError):
            cad.execute(self.job, Path('/tmp'))


if __name__ == '__main__':
    unittest.main()
