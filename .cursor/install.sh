#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for predykcja-gazu.
# Safe to run repeatedly and against cached or snapshotted state.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR="${REPO_ROOT}/.venv"

# The default Cloud Agent image can ship CPython without ensurepip/venv.
if ! python3 -c "import ensurepip, venv" >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y --no-install-recommends python3-venv
fi

if [ ! -x "${VENV_DIR}/bin/python" ]; then
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip

# The repository currently has no dependency manifests. Keep these optional.
for req in requirements.txt requirements-dev.txt; do
  if [ -f "${REPO_ROOT}/${req}" ]; then
    python -m pip install -r "${REPO_ROOT}/${req}"
  fi
done

python --version
echo "install.sh: development environment ready (venv at ${VENV_DIR})"
