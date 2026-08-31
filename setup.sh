#!/usr/bin/env bash
# Полная сборка проекта Courses_projects на Ubuntu:
#   - системные зависимости (Python 3, venv, Node.js/npm)
#   - backend: виртуальное окружение, зависимости, миграции БД
#   - frontend: npm-зависимости и production-сборка (Vite)
#
# Использование:
#   ./setup.sh              — полная сборка backend + frontend
#   ./setup.sh --skip-node  — не проверять/не ставить Node.js (если он уже настроен)
#
# Для автоматического создания суперпользователя Django задайте перед запуском:
#   DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

NODE_MIN_MAJOR=20
NODE_MIN_MINOR=19
SKIP_NODE=false

for arg in "$@"; do
  case "$arg" in
    --skip-node) SKIP_NODE=true ;;
    *) echo "Неизвестный аргумент: $arg" >&2; exit 1 ;;
  esac
done

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$1"; }
warn() { printf '\033[1;33m[!] %s\033[0m\n' "$1" >&2; }
err()  { printf '\033[1;31m[x] %s\033[0m\n' "$1" >&2; }

trap 'err "Сборка прервана из-за ошибки (строка $LINENO)"' ERR

apt_install() {
  log "Устанавливаю через apt: $*"
  sudo apt-get update -qq
  sudo apt-get install -y "$@"
}

# ---------------------------------------------------------------------------
# 1. Системные зависимости
# ---------------------------------------------------------------------------

log "Проверка системных зависимостей"

if ! command -v python3 >/dev/null 2>&1; then
  apt_install python3
fi

PY_MINOR="$(python3 -c 'import sys; print(sys.version_info[1])')"
if [ "$PY_MINOR" -lt 10 ]; then
  err "Требуется Python 3.10+, найден 3.$PY_MINOR"
  exit 1
fi

if ! python3 -m pip --version >/dev/null 2>&1; then
  apt_install python3-pip
fi

if [ "$SKIP_NODE" = false ]; then
  NEED_NODE_INSTALL=false
  if ! command -v node >/dev/null 2>&1; then
    NEED_NODE_INSTALL=true
  else
    NODE_MAJOR="$(node -e 'console.log(process.versions.node.split(".")[0])')"
    NODE_MINOR="$(node -e 'console.log(process.versions.node.split(".")[1])')"
    if [ "$NODE_MAJOR" -lt "$NODE_MIN_MAJOR" ] || { [ "$NODE_MAJOR" -eq "$NODE_MIN_MAJOR" ] && [ "$NODE_MINOR" -lt "$NODE_MIN_MINOR" ]; }; then
      NEED_NODE_INSTALL=true
    fi
  fi

  if [ "$NEED_NODE_INSTALL" = true ]; then
    log "Node.js отсутствует или старее требуемой версии (>= ${NODE_MIN_MAJOR}.${NODE_MIN_MINOR}). Устанавливаю Node.js 22.x через NodeSource"
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    apt_install nodejs
  fi

  command -v npm >/dev/null 2>&1 || { err "npm не найден после установки Node.js"; exit 1; }
fi

log "Версии инструментов"
python3 --version
[ "$SKIP_NODE" = true ] || { node --version; npm --version; }

# ---------------------------------------------------------------------------
# 2. Backend (Django)
# ---------------------------------------------------------------------------

log "Настройка backend (Django)"

if [ ! -d ".venv" ]; then
  log "Создаю виртуальное окружение .venv"
  if ! python3 -m venv .venv; then
    apt_install "python3-venv"
    python3 -m venv .venv
  fi
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

mkdir -p media

log "Проверка проекта Django (manage.py check)"
python manage.py check

log "Применение миграций базы данных"
python manage.py migrate --noinput

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  log "Создание суперпользователя '${DJANGO_SUPERUSER_USERNAME}'"
  python manage.py createsuperuser --noinput \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" \
    || warn "Суперпользователь уже существует или произошла ошибка при создании"
fi

deactivate

# ---------------------------------------------------------------------------
# 3. Frontend (React + Vite)
# ---------------------------------------------------------------------------

if [ "$SKIP_NODE" = false ]; then
  log "Настройка frontend (React + Vite)"
  cd "$ROOT_DIR/frontend"

  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install
  fi

  npm run build

  cd "$ROOT_DIR"
else
  warn "Frontend пропущен (--skip-node)"
fi

# ---------------------------------------------------------------------------
# Итог
# ---------------------------------------------------------------------------

log "Сборка завершена успешно"

cat <<EOF

Backend:
  source .venv/bin/activate && python manage.py runserver

Frontend (dev-сервер):
  cd frontend && npm run dev

Frontend (production-сборка):
  готова в frontend/dist/

Запустить backend + frontend dev-сервер одновременно:
  ./run.sh
EOF
