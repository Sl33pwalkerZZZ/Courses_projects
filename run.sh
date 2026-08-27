#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
  echo "Останавливаю процессы..."
  jobs -p | xargs -r kill
}
trap cleanup EXIT INT TERM

# --- Backend (Django) ---
cd "$ROOT_DIR"
source .venv/bin/activate
python manage.py runserver &

# --- Frontend (Vite) ---
cd "$ROOT_DIR/frontend"
npm run dev &

wait
