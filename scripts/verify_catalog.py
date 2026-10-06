"""Verify the offline catalog, its existing tests and representative CLI queries."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def lookup(*args):
    return json.loads(subprocess.check_output(
        [sys.executable, str(ROOT / 'tools/query.py'), *args, '--brief', '--json'],
        cwd=ROOT, text=True,
    ))


def main():
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                   cwd=ROOT, check=True)
    catalog = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
    expected = {'product': 78, 'stone': 135, 'wood': 7, 'leather': 72, 'fabric': 108}
    assert len(catalog['records']) == 400
    assert dict(Counter(r['kind'] for r in catalog['records'])) == expected
    print('Catalog: 400 records', expected)
    cases = [
        (['Adler', '--kind', 'product'], 1),
        (['1224 Outdoor', '--kind', 'product'], 1),
        (['--kind', 'stone', '--color', '蓝色', '--limit', '20'], 14),
        (['--kind', 'product', '--format', '3ds'], 6),
        (['Tadao III', '--kind', 'product'], 1),
        (['Tadao V', '--kind', 'product'], 1),
        (['MOVE 1372', '--kind', 'product'], 1),
        (['2078', '--kind', 'product'], 1),
    ]
    for args, count in cases:
        result = lookup(*args)
        assert result['total_matched'] == count, (args, result['total_matched'])
        print('Query:', ' '.join(args), '=>', count)
    # The numeric family is indexed; V/VI evidence lives in the companion note.
    assert lookup('2078-V', '--kind', 'product')['total_matched'] == 0
    note = (ROOT / 'knowledge/nobile-bar-2078.md').read_text(encoding='utf-8')
    assert '2078-VI' in note and '2078-V' in note and '2078_VI_NOBILE_BAR.zip' in note
    print('Known limitation: 2078-V needs the 2078 family query and companion note.')
    source = subprocess.check_output([
        sys.executable, str(ROOT / 'tools/source.py'),
        'https://draenert.de/de/material/stein/bianco-lila.html',
    ], cwd=ROOT, text=True)
    assert 'Bianco Lila' in source and 'L32:' in source
    print('Archived source lookup passed; live stock and ZIP contents were not checked.')


if __name__ == '__main__':
    main()
