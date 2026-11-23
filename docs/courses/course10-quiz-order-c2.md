# Course 10 — C2 pinned choice-order correction

Дата:2026-11-23. Ветка feat/studio-course-authoring, исходный HEAD4bf1338. C1 сохранён; рабочая база и локальный config/settings.py не изменялись.

## Актуальное состояние и схема

Read-only SQLite mode=ro: Course10/ai-media-content неопубликован; Quiz5,lesson116,module order6/lesson order1, опубликован;15вопросов,60вариантов,70%,попыток0. Вопросы/варианты сверены с каноническим Module6 JSON. Нет чтения содержимого работ или персональных результатов.

QuizChoice:integer PK AUTOINCREMENT,question FK, text,is_correct,integer order с CHECK>=0; index question_id; нет unique(question,order). ORM Meta ordering=[order,pk]. Правильность хранится в is_correct; сервер оценивает выбранные IDs, а QuizAnswer хранит исторические snapshots. Миграции не нужны.

Обычный Studio PUT запрещает опубликованные/оценённые тесты и пересоздаёт вопросы/варианты. Он не вызывается; его ограничения для обычного редактирования остаются. Это отдельно разрешённая узкая операторская C2-коррекция только порядка, не универсальное снятие блокировки.

## Операция

- courses/management/course10_quiz5_order.json: точный снимок quiz/questions/choices, прежние IDs/связи/тексты/ключи/order и целевые order.
- reorder_course10_quiz5: default dry-run; exact Course10+Quiz5+lesson116 scope, метаданные70%/publication, вопросы и все60вариантов должны совпасть полностью с before либо полностью с after.
- Любое частичное применение, изменение текста/ключей/IDs/связей/порога/публикации или канонического источника — STOP.
- Если до перехода появились попытки — STOP и новый review. История не удаляется. Если permutation уже применена, KEEP допускается и после новых попыток.
- Только QuizChoice.order обновляется на месте:32поля; число записей, все IDs, ключи, вопросы, истории и статусы неизменны.
- SQLite IMMEDIATE write reservation → повторная валидация → существующий create_backup (online backup API,0600,integrity/FK) → атомарные условные updates → проверка exact after. Ошибка откатывает всю транзакцию. Повторный запуск без записей/нового backup.
- Канонический quiz в media_module_6.json получил только соответствующие перестановки choices для будущего импорта. Тексты, ключи, порог и C1 lesson/assignment побайтово сохранены. Этот create-only импортёр не использовать как обновлятор существующего теста.

## Позиции правильных ответов

Это операторская таблица для владельца, не студенческий API и не учебная подсказка.

| Вопрос по порядку | До | После |
|---|---:|---:|
| 1 | 1 | 2 |
| 2 | 1 | 4 |
| 3 | 1 | 1 |
| 4 | 1 | 3 |
| 5 | 1 | 1 |
| 6 | 1 | 2 |
| 7 | 1 | 4 |
| 8 | 1 | 3 |
| 9 | 1 | 2 |
| 10 | 1 | 1 |
| 11 | 1 | 3 |
| 12 | 1 | 4 |
| 13 | 1 | 3 |
| 14 | 1 | 2 |
| 15 | 1 | 1 |

Итого позиции1/2/3/4:4/4/4/3 — максимально равномерно для15вопросов. Остальные варианты сохраняют взаимный порядок.

## Проверка

- /tmp/course10-c2/copy.sqlite3: согласованная копия рабочей SQLite через backup API с mode=ro источником. Копия и временные артефакты не являются постоянным архивом.
- На копии создан только синтетический студент/enrollment; перед изменением сделан полный снимок таблиц. Синтетические проверки оценки до перестановки выполнялись внутри rollback-транзакции без удаления истории.
- На копии повторены production-примитивы IMMEDIATE/plan/create_backup/write_orders/postcheck. CLI --apply не запускался. Ветка команды --apply проверена только в disposable unit test DB с mock backup; настоящий backup отдельно проверен на копии.
- Полное сравнение до/после: только32 QuizChoice.order; все другие строки/поля идентичны, включая Course8, Course10/C1-тексты, публикацию, политики сертификатов, вопросы, ключи и историю.
- Реальный student LessonQuizView: ID каждого варианта тот же, порядок изменён, order1–4, is_correct не раскрывается.
- Подсчёт до/после:10/15=66.67%,passed=False;11/15=73.33%,passed=True. Прежние choice IDs продолжают оцениваться по тем же ключам.
- После новых синтетических попыток KEEP; snapshots/результаты не меняются. Отдельный тест подтверждает STOP без изменения истории, если попытка появилась перед первоначальным применением.
- Backup и копия: integrity_check=ok,foreign_key_check=0. Результаты: /tmp/course10-c2/results.json; backup path в этом приватном локальном файле.
-69Django tests passed:8новых C2 + C1/import/Studio quiz/quiz regressions. Django check,git diff --check passed. Native security_reviewer выполнил read-only review, блокеров не найдено; тесты им не запускались.
- Рабочая SQLite/settings SHA-256 совпадают с исходными; рабочий Course10 draft,Quiz5/order исходные,попыток0. Index пуст. Frontend/медиа не менялись; браузерный прогон/lint/build не запускались.

Команды проверок (settings_c2 — временный модуль с default=/tmp/course10-c2/copy.sqlite3, TEST=:memory:; settings_ro — рабочая база исключительно mode=ro):

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/course10-c2:$PWD DJANGO_SETTINGS_MODULE=settings_c2 .venv/bin/python -B manage.py test courses.test_quiz5_order courses.test_course10_editorial courses.test_module6_import studio.test_quiz_authoring quizzes.tests --verbosity 1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/course10-c2:$PWD DJANGO_SETTINGS_MODULE=settings_ro .venv/bin/python -B manage.py reorder_course10_quiz5 --dry-run
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/course10-c2:$PWD DJANGO_SETTINGS_MODULE=settings_ro .venv/bin/python -B manage.py check
git diff --check
```

## Безопасное рабочее применение — только после отдельного разрешения

Закрыть редактирование/тестирование курса на время операции; повторно проверить число попыток. Ожидаемый план: UPDATE32order/0других полей/attempt_count0. При ином плане не продолжать. Команда сама создаёт и проверяет новый backup; не перезаписывает прежние.

```bash
.venv/bin/python -B manage.py reorder_course10_quiz5 --dry-run
.venv/bin/python -B manage.py reorder_course10_quiz5 --apply --backup-dir .local-course-backups/course10-c2
.venv/bin/python -B manage.py reorder_course10_quiz5 --dry-run
```

Здесь рабочий --apply НЕ выполнен. Ожидается KEEP0 после применения, затем проверка student API. Курс10 не публикуется, Quiz5 не снимается с публикации, C1 не применяется этой командой. Откат не делать восстановлением всей базы поверх новых данных; отдельно согласовать точечный обратный порядок и учитывать новые попытки. Не использовать Studio PUT, не пересоздавать вопросы/варианты.

## Изменённые файлы

- courses/management/commands/reorder_course10_quiz5.py
- courses/management/course10_quiz5_order.json
- courses/management/media_module_6.json (только перестановки choices)
- courses/test_quiz5_order.py
- docs/courses/course10-quiz-order-c2.md
- docs/project-memory/CURRENT_STATE.md
- docs/project-memory/DECISIONS.md
