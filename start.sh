#!/usr/bin/env bash
set -euo pipefail

# Render start script: logs environment and starts gunicorn bound to $PORT
echo "========== START: PG Buddy start.sh =========="
echo "User: $(whoami)"
echo "Python: $(which python)"
echo "Gunicorn version: $(gunicorn --version 2>/dev/null || echo 'gunicorn not found')"
echo "Environment variables:"
echo "  PORT=${PORT:-<not set>}"
echo "  FLASK_DEBUG=${FLASK_DEBUG:-<not set>}"
echo "  PG_BUDDY_SECRET=${PG_BUDDY_SECRET:+<set>}"

if [ -z "${PORT:-}" ]; then
  echo "PORT not set, defaulting to 5000"
  PORT=5000
fi

echo "Listening ports before starting gunicorn:"
if command -v ss >/dev/null 2>&1; then
  ss -ltnp || true
else
  netstat -ltnp 2>/dev/null || true
fi

WORKERS=1

echo "Starting gunicorn bound to 0.0.0.0:$PORT with $WORKERS worker(s)"
exec gunicorn app:app \
  --workers "$WORKERS" \
  --bind 0.0.0.0:$PORT \
  --access-logfile - \
  --error-logfile - \
  --capture-output
