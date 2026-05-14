#!/bin/bash
# SessionStart hook for Claude Code on the web.
# 1. Displays active requirements from PROCESS.md (always — local and remote).
# 2. Installs Python dependencies so pytest can run (remote sessions only).
# Local sessions skip dependency install — assume the user manages their own venv.

set -euo pipefail

cd "$CLAUDE_PROJECT_DIR"

# Display active requirements (always — local and remote)
if [ -f "PROCESS.md" ]; then
  echo "📋 PROCESS.md — דרישות פתוחות:"
  awk '/^## דרישות פתוחות/,/^## דרישות סגורות/' PROCESS.md | head -30
  echo ""
fi

# Dependency install — only on remote sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

python3 -m pip install --quiet --upgrade pip || true  # soft-fail if pip can't self-upgrade
python3 -m pip install --quiet -r requirements.txt
