#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p inputs work outputs
.venv/bin/python - <<'PY'
from pathlib import Path
import ezdxf
import openpyxl
import docx
import pptx
import pypdf
import PIL
import matplotlib

target = Path('work/environment-smoke-test.dxf')
doc = ezdxf.new('R2018')
doc.units = 4  # Explicit millimetres for this synthetic test only.
doc.modelspace().add_lwpolyline([(0, 0), (1000, 0), (1000, 1000), (0, 1000)], close=True)
doc.saveas(target)
result = ezdxf.readfile(target)
assert result.dxfversion == 'AC1032'
assert result.units == 4
assert len(result.modelspace().query('LWPOLYLINE')) == 1
print('Dependency imports and R2018 DXF round-trip passed.')
print('Chinese document rendering and desktop application compatibility still require verification.')
PY
.venv/bin/python -m pip freeze > work/installed-packages.txt
