#!/usr/bin/env bash
# Idempotent development bootstrap for the predykcja-gazu Python project.
# Safe to run repeatedly and against cached/snapshotted state.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR="${REPO_ROOT}/.venv"

# The default Cloud Agent image ships CPython without the venv/ensurepip module.
# Install it once if virtual environments cannot be created yet.
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y --no-install-recommends "python3-venv"
fi

if [ ! -x "${VENV_DIR}/bin/python" ]; then
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip

# Install project dependencies when a requirements file is present. The current
# application (.cursor/skills/gold-prediction/scripts/score_gold.py) is
# stdlib-only, so these are guarded and optional.
for req in requirements.txt requirements-dev.txt; do
  if [ -f "${REPO_ROOT}/${req}" ]; then
    python -m pip install -r "${REPO_ROOT}/${req}"
  fi
done

python --version
echo "install.sh: development environment ready (venv at ${VENV_DIR})"
