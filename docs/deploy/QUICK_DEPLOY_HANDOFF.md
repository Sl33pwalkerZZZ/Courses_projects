# AI Courses — quick deployment handoff

Дата: 2026-11-26. Repository: https://github.com/Sl33pwalkerZZZ/Courses_projects

Release branch: `release/ai-courses-v1`. **Локально подготовлена; push заблокирован проверкой безопасности. Не считать ветку доступной на GitHub или deployment завершённым.**

## Стоп-условия перед deployment

1. В старой Git-истории `config/settings.py:23` находится используемый literal Django `SECRET_KEY`; он уже присутствует в `origin/master`. Не печатать и не копировать его в production. Нужны отдельно разрешённые внешние production settings и новый случайный ключ. Ротация инвалидирует прежние JWT/сессии. История не переписывалась; удаление строки новым коммитом не устраняет прежнее раскрытие. По текущему заданию settings запрещено менять, поэтому release push остановлен.
2. Реальный Groq smoke test с локальным ключом получил **HTTP401** после добавления нормального User-Agent. Нужен действующий GroqCloud API key в защищённом окружении backend. Не присылать ключ в чат/GitHub, не использовать `VITE_*` для секрета. Предыдущий запрос default Python urllib UA получил403; клиент теперь идентифицируется `AI-Courses-Guide/1.0`.
3. Рабочая SQLite, защищённые файлы и production-конфигурация не входят в Git. До переноса владелец должен предоставить согласованный приватный backup и разрешить перенос. Без этого новый deployment будет пустым. Не создавать/публиковать Course10 автоматически.

## Проверенный стек и установка

- Python: используйте совместимую с `Django==6.1` версию (локально Python3.13); зависимости точно в `requirements.txt`.
- Node24 локально проверен; Vite8 требует поддерживаемый современный Node. Frontend lockfile уже в репозитории.
- Runtime web server: Gunicorn не входит в текущие application requirements; hosting должен предоставить его или установить отдельно. Не считать Django runserver production server.

После разрешённого push:

```bash
git clone --branch release/ai-courses-v1 https://github.com/Sl33pwalkerZZZ/Courses_projects.git
cd Courses_projects
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd frontend
npm ci
VITE_API_URL=/api npm run build
```

Frontend output: `frontend/dist`. Секреты из root `.env` не нужны frontend build.

## Vercel: frontend и same-origin API

Project root: `frontend`, build: `npm run build`, output: `dist`, environment **`VITE_API_URL=/api`** (точное существующее имя). Изменение build variable требует rebuild.

Настройте rewrite `/api/:path*` на `https://YOUR-BACKEND/api/:path*`, затем SPA fallback остальных маршрутов на `/index.html`. Это конфигурация hosting, не уже добавленный `vercel.json`. Реальный backend URL выбирает команда; не оставлять literal YOUR-BACKEND.

**Важно:** защищённый video playback использует same-origin cookie. Прямой `VITE_API_URL=https://other-origin/...` не эквивалентен rewrite и может сломать playback. Proxy должен сохранять `Authorization`, `Set-Cookie`, `Range`, ответы206, `Content-Range`, `Content-Disposition`, `Vary` и private/no-store. Отключить shared/CDN caching для `/api/*`, включая AI Guide. Не открывать `MEDIA_ROOT` публичным static rewrite.

## Backend settings и запуск

`config/settings.py` — существующие dev settings, не безопасная production-конфигурация. Большинство значений сейчас **не читается из env**: простого добавления `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS` или `DATABASE_URL` недостаточно. Их должен прочитать отдельный production settings module, создаваемый teammate после разрешения владельца. В этом релизе такой модуль не добавлен, local settings сохранены.

Минимальные overrides этого модуля:

| Параметр Django | Обязательное решение deployment |
|---|---|
| `SECRET_KEY` | Новый случайный секрет из secret manager/env; никогда старый tracked key |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | Точные backend/frontend hostnames, без схемы и wildcard |
| `DATABASES` | Persistent SQLite path или отдельно спланированный переход на PostgreSQL; `DATABASE_URL` сам не разбирается текущим кодом |
| `MEDIA_ROOT` | Постоянный приватный каталог, совпадающий с восстановленными путями БД |
| `PUBLIC_MEDIA_ROOT` | Отдельный постоянный публичный каталог; не пересекать с private root |
| `STATIC_ROOT` | Каталог для `collectstatic`, подключённый hosting static delivery |
| `CACHES` | Общий cache для нескольких workers, иначе guide throttle локален каждому процессу |
| `CORS_ALLOWED_ORIGINS` | Точные HTTPS origins при реальных cross-origin запросах; не `allow all` |
| `CSRF_TRUSTED_ORIGINS` | Точные HTTPS origins для Django admin/session flows |
| HTTPS/cookies | Secure session/CSRF/playback transport, корректный доверенный proxy scheme; HSTS после проверки HTTPS |
| `CERTIFICATES_ENABLED` | Оставить `False`; сертификаты не включать в этом задании |

Названия env для production (`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `SQLITE_PATH`, `MEDIA_ROOT`, etc.) — договор deployment-модуля, **не уже поддерживаемые переменные текущих dev settings**. Не добавлять их молча и ожидать эффекта. Если используется `SECURE_PROXY_SSL_HEADER`, доверять только контролируемому ingress, который удаляет пользовательскую подделку forwarded headers.

Команды после подготовки settings module (заменить `YOUR_PRODUCTION_SETTINGS` на реально созданный module):

```bash
DJANGO_SETTINGS_MODULE=YOUR_PRODUCTION_SETTINGS .venv/bin/python manage.py check --deploy
DJANGO_SETTINGS_MODULE=YOUR_PRODUCTION_SETTINGS .venv/bin/python manage.py showmigrations
# Перед migrate: consistent backup целевой БД + media, проверить реальный DB path.
DJANGO_SETTINGS_MODULE=YOUR_PRODUCTION_SETTINGS .venv/bin/python manage.py migrate --plan
DJANGO_SETTINGS_MODULE=YOUR_PRODUCTION_SETTINGS .venv/bin/python manage.py migrate --noinput
DJANGO_SETTINGS_MODULE=YOUR_PRODUCTION_SETTINGS .venv/bin/python manage.py collectstatic --noinput
DJANGO_SETTINGS_MODULE=YOUR_PRODUCTION_SETTINGS .venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 60
```

Не выполнять эти шаблонные команды на рабочей локальной SQLite. Сначала rehearsal на изолированной копии. В production перенос существующего курса — восстановление согласованной БД/файлов, а не безусловный повторный importer/создание курса. Проверить integrity/FK и publication Course10=False. SQLite требует persistent writable volume, один экземпляр приложения и резервное копирование SQLite backup API; ephemeral filesystem hosting непригоден.

Для локального development уже существует `.venv/bin/python manage.py runserver 127.0.0.1:8000`; текущий Vite dev proxy направляет `/api` туда. Он не является isolated test server.

## Groq AI Guide

Фактически поддерживаются backend env:

```text
GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-20b
DJANGO_SETTINGS_MODULE  # стандартный Django выбор module
```

В dev allowlist loader читает только две GROQ переменные из root `.env`, если они не заданы в process env; без shell/interpolation. В production предпочтителен secret manager/process env. Пустой process env намеренно перекрывает `.env`. `.env`, `.env.*` игнорируются Git; `.env.example` исключение не содержит реального ключа. Editor swap `..env.swp` также нельзя добавлять/передавать.

Endpoint: **POST `/api/ai-guide/`**, `Authorization: Bearer <current access JWT>`, JSON `{lesson_id, question, language}`. Question backend1–2000 chars, UI до1000; language ru/kk/en. Только существующий доступ к уроку (зачисление/владелец/модератор), не публичный catalog access. Контекст берётся сервером: title/text текущего урока до16000 chars. Никаких client lesson body, quiz keys, instructor notes, submissions или attachment credentials. Ответ `{answer}`; no-store; timeout25s; output bounded;12/min/user.

Это **не RAG**, не multi-turn server memory, не проверка работ. История только React state до смены урока/сессии, до20 пар; не сохраняется в БД. Модель должна различать материал урока и общие знания, но её ответы могут ошибаться. Защита от выдачи настоящих quiz keys обеспечивается отсутствием ключей в запросе; абсолютной гарантии, что общая модель не решит учебную задачу сама, нет.

Smoke test после настройки:

1. Войти синтетическим студентом на изолированном rehearsal, получить доступ к синтетическому уроку без персональных данных.
2. Нажать AI-помощник → отправить короткий вопрос → увидеть ответ; в Network должен быть200 от `/api/ai-guide/`, без ключа.
3. Проверить очистку, переход к другому уроку/выход, ошибки и лимит; чужой пользователь не должен получить контекст.
4. Для внешнего Groq включить действующий backend key; не логировать Authorization, prompt, ответы студента или root.env. HTTP401 означает отклонённый ключ,429 — лимит провайдера,502/504 — безопасно обработанный сбой/timeout.

## Медиа и курс

Перенести приватно все файлы, на которые ссылаются restored DB attachments/images/submissions, сохраняя относительные пути и SHA-256. Module5 финальные9MP4/VTT не скачиваются из Git. Не использовать случайные previews вместо финалов. Проверить реальные Range/seek, captions, permissions после HTTPS proxy. Public assets выдавать отдельно; каталоги `lessons`/`submissions` не должны становиться публичными.

Course8 не менять; Course10 остаётся draft. Publication acknowledgement/request/admin approval — отдельный авторизованный этап. Certificates остаются выключены; issuer/origin/policy не настраивались.

## Результаты этого этапа

- D5 сохранён локально: `1cd2f7f` — `feat: redesign course catalog and course details`, ровно30 путей из D5 плана.
- AI Guide: backend23/23 (15 новых +8 существующих course authorization), frontend focused51/51, полныйfrontend475/475, lint/build/system check/whitespace — результаты финальной проверки. Поведение финального `/api/ai-guide/` дополнительно проверено отдельно; route не перехватывает course slug `ai-guide`.
- Chromium с настоящими Django8210, Vite5210, изолированной пустой SQLite/media и синтетическими аккаунтами: RU dark1440, KK light375, EN dark320. External provider в этом браузерном окружении заменён явно синтетическим adapter; это проверка UI/API, **не успешный ответ Groq**. Loading, ответ, сохранение вопроса при502, очистка, отмена pending, reset при смене урока,401anonymous/403outsider и отсутствие overflow проверены. Финальные machine-readable результаты временно в `/tmp/ai-release-browser/results.json`.
- Браузер выявил и помог исправить одинаковые sibling keys AI Guide/Quiz; лишний key убран, родительский reset по lesson/session сохранён, regression добавлен. Финальные прогоны выполнялись после полной загрузки, не на испорченном HMR DOM.
- Реальный Groq запрос отправлял только синтетический несекретный контекст. Финальный HTTP401: локальный ключ из root.env присутствует и имеет ожидаемую форму, но провайдер его отклонил. Секрет не выводился, в browser/build не передаётся. End-to-end external LLM success **не подтверждён**.
- Независимый security review: новых доступных auth/context утечек в AI пути не обнаружено. Push всё равно **BLOCKED** старым используемым tracked SECRET_KEY. Просмотрены2562 Git blobs всех refs; backup SQLite blob найден только в другом недостижимом из release ref, не включается в отправку. Нельзя использовать `--all`/`--mirror`.
- Никаких новых моделей/миграций, изменений рабочей SQLite, настроек или publication/сертификатных правил. Все117 исходных защищаемых hash совпали; SQLite integrityOK/FK0, Course8published=True/Course10published=False. Итоговая проверка записана в project-memory. Локальные `.env` и swap исключены из Git; рабочие untracked материалы сохранены.

Backend verification воспроизводится только с отдельными test settings/БД. В выполненном прогоне временный `ai_guide_test_settings` задавал SQLite `:memory:`, LocMem cache и `/tmp/ai-guide-test-media`:

```bash
PYTHONPATH=/tmp:$PWD .venv/bin/python manage.py test courses.test_ai_guide courses.tests --settings=ai_guide_test_settings --noinput
cd frontend
node --test tests/ai-guide.test.mjs tests/lesson-workspace.test.mjs
node --test tests/*.test.mjs
npm run lint
npm run build
```

Временный test module не входит в Git: teammate должен создать эквивалент вне репозитория прежде запуска, а не направлять команды на production settings. Адаптер использует только stdlib, новых Python/JS зависимостей нет.

Groq API/model параметры сверены с [официальной API reference](https://console.groq.com/docs/api-reference) и [GPT-OSS reasoning documentation](https://console.groq.com/docs/reasoning): отдаётся только `message.content`, `include_reasoning=false`, неподдерживаемый для20b `reasoning_format` не используется.

Deployment не выполнен. Никакие секреты, рабочая SQLite, приватные uploads или backups не отправлены на GitHub.
