#!/usr/bin/env bash
# Запускает backend (Django) и открывает админ-консоль в браузере.
#
# Админка живёт на встроенном django.contrib.admin: /admin/
# (см. config/urls.py). Отдельного процесса для неё не нужно —
# это просто ещё один маршрут на том же сервере.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="127.0.0.1"
PORT="8000"
ADMIN_URL="http://${HOST}:${PORT}/admin/"

cleanup() {
  echo "Останавливаю сервер..."
  jobs -p | xargs -r kill
}
trap cleanup EXIT INT TERM

cd "$ROOT_DIR"
source .venv/bin/activate

python manage.py runserver "${HOST}:${PORT}" &
SERVER_PID=$!

echo "Жду запуска сервера..."
for _ in $(seq 1 30); do
  if curl -s -o /dev/null "http://${HOST}:${PORT}/admin/login/"; then
    break
  fi
  sleep 0.5
done

echo "Открываю админ-консоль: ${ADMIN_URL}"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$ADMIN_URL" >/dev/null 2>&1 &
else
  echo "Не удалось найти xdg-open — открой ссылку вручную: ${ADMIN_URL}"
fi

wait "$SERVER_PID"
