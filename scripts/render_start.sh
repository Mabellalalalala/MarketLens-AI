#!/bin/sh
set -eu
if [ ! -f data/snapshots/latest.json ]; then
  echo "No Research Snapshot found; attempting server-side build"
  PYTHONPATH=src python scripts/build_snapshot.py || echo "Snapshot build failed; app will expose UNAVAILABLE state"
fi
exec gunicorn --chdir src marketlens_ai.app:app --bind "0.0.0.0:${PORT:-10000}" --workers 1 --timeout 120
