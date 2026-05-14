#!/bin/bash
set -euo pipefail

# Claude Code Session Start Hook
# Installs Python dependencies from requirements.txt

echo "🔧 Installing Python dependencies..."
pip install -q -r requirements.txt 2>/dev/null || true

echo "✅ Session initialization complete"
