#!/usr/bin/env bash
# Source this file to retain the working directory and writable cache settings.
set -euo pipefail
umask 077
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p inputs work outputs work/.cache work/.mpl
export XDG_CACHE_HOME="$PWD/work/.cache"
export PIP_CACHE_DIR="$PWD/work/.cache/pip"
export MPLCONFIGDIR="$PWD/work/.mpl"
test -x .venv/bin/python
.venv/bin/python -m pip check
.venv/bin/python - <<'PY'
import ezdxf, openpyxl, docx, pptx, pypdf, PIL, matplotlib
print('Interior design dependency imports passed.')
PY
command -v soffice
command -v pdftoppm
command -v pdftotext
test -r /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
soffice --version
pdftoppm -v
printf '%s\n' 'File-processing environment ready; no persistent server is required.'
