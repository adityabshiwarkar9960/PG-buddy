#!/usr/bin/env bash
set -e

: "Print environment and start gunicorn bound to PORT"

echo "Starting PG Buddy"
echo "PORT=${PORT:-<not set>}"
if [ -z "$PORT" ]; then
  echo "PORT not set, defaulting to 5000"
  PORT=5000
fi

exec gunicorn app:app --workers 3 --bind 0.0.0.0:$PORT
