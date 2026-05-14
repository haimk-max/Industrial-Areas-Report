#!/bin/bash
# SessionStart hook for Claude Code on the web.
# Installs Python dependencies so pytest can run on session start.
# Local sessions (non-remote) skip this — assume the user manages their own venv.

set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r requirements.txt
