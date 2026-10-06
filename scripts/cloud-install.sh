#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p inputs work outputs work/.cache work/.mpl
export XDG_CACHE_HOME="$PWD/work/.cache"
export PIP_CACHE_DIR="$PWD/work/.cache/pip"
export MPLCONFIGDIR="$PWD/work/.mpl"
test -x .venv/bin/python || python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-cloud.lock
source scripts/cloud-start.sh
