# P1F — диагностика отсутствующего сертификата и SQLite safety

Дата: 2026-11-13, Asia/Almaty. Ветка `design/amethyst-motion`, HEAD `e1ae750`, ahead4 по локальной origin reference. Ни staging, ни commit/push не выполнялись.

## Подтверждённые факты

- Активные Django settings указывают на `/home/almas/Desktop/courses/Courses_projects/db.sqlite3`, SQLite, размер1,384,448bytes.
- В базе ровно один Certificate: Course8, owner user ID2, выдан2026-10-27, не отозван. Имя, issuer snapshot и evidence присутствуют; их значения и полный verification identifier не выводились.
- ID аккаунта `student` —2: ownership совпадает с этим **предполагаемым аккаунтом**, но активный browser-account не установлен. Угадывать его по базе нельзя.
- Runtime `CERTIFICATES_ENABLED=False`. В `certificates/views.py::CertificateView.initial` глобальный gate возвращает404 до чтения Certificate. Он действует на MyCertificates, download/status/verify, а не только на новую выдачу.
- `MyCertificates.get` при включённом gate фильтрует только `student=request.user`; не требует новой name confirmation, опубликованности курса, активной policy или повторной eligibility для списка уже выданных snapshot. Profile монтирует MyCertificates и не фильтрует issued records. Изолированные тесты это подтверждают.
- CertificateName API расположен отдельно от глобального certificate gate, поэтому имя можно сохранить/подтвердить при недоступном списке сертификатов. Это объясняет наблюдаемое сочетание экранов без гипотезы об удалении Certificate.

## Причина и узкий fix

Приложение намеренно закрывает certificate API глобальным gate. Frontend `useCertificateRead` ранее превращал404 `/my/certificates/` в `[]`; Profile показывал настоящий empty state вместо недоступности сервиса. Именно эта детерминированная ошибка отображения исправлена.

Теперь404 оставляет состояние `enabled:false`, и Profile показывает отдельную RU/KK/EN строку «Раздел сертификатов сейчас недоступен». Настоящий200 `[]` по-прежнему означает пустую историю;401/403/5xx/network остаются error/retry, не становятся пустым списком. Existing issued/revoked cards не фильтруются. Session generation и refresh protections не менялись.

**Сертификат не станет виден автоматически от этого UI-fix:** глобальный gate сохранён. Не включались ни глобальная выдача, ни policy/issuer. Требуется отдельное решение владельца: сохранить текущий общий запрет либо отдельно спроектировать доступ к существующим issued snapshots при отключённой новой выдаче. Простое включение global flag меняет доступность всего certificate API и не выполнялось. Переиздавать Certificate или изменять ownership оснований нет.

## Свежий backup

Создан до изменений приложения через SQLite backup API из source `mode=ro`, `PRAGMA query_only=ON`:

`/home/almas/Desktop/courses/Courses_projects/.local-course-backups/p1f-20261113T040236040248Z/db.sqlite3`

Source integrity ok, FK0. Backup integrity ok, FK0; основные counts source/backup совпали: courses10, modules39, lessons115, users3, enrollments6, submissions1, quiz attempts4, certificates1. Содержимое отправок/имён/учётных данных в отчёт не включено.

Рабочая SQLite SHA-256 до и после: `f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e`. Размер и hash неизменны. Hash backup-файла отличается из-за сериализации SQLite backup, это не проверка побитового cp; проверены SQLite integrity, FK и логические counts. Backup создан с ограниченными правами через umask077; рабочая БД не заменялась.

## Историческая смена hash

Текущий hash совпадает с P1E и отличается от более раннего P1D `3c45b29b552d7b4ef5f9b78c672c8146317b42c6ab0257cc2c2ef4e105e4ecb3`. Смена hash сама по себе не означает повреждение.

Проверены read-only две доступные исторические копии:

- `.local-course-backups/media-module-before-f7fbd0bc4b1d4fc78110b67a5f74c09f.sqlite3` — integrity ok; Course8 certificate ownership/course/issued/revoked values совпадают. У user2 отличаются только из проверенных полей `certificate_name`, `certificate_name_confirmed_at`; `last_login` совпадает.
- `backups/pre-migrations/db-before-migrations-20261111-091224.sqlite3` — integrity ok; тот же Course8 certificate identity/status; новых certificate-name колонок ещё нет.

В текущей базе certificate name заполнен, server confirmation timestamp —2026-11-12 UTC. Это согласуется с сообщением владельца о сохранении имени и представляет подтверждённое легитимное изменение относительно доступной копии. Точной копии именно старого P1D hash не установлено, поэтому **не доказано**, что только эти поля объясняют все различия bytes. Другие пользовательские записи/содержимое отправок не исследовались.

## Изменённые P1F файлы

- `frontend/src/components/certificates/Certificates.jsx`: различение unavailable и empty; тестируемый presentation component CertificateListContent.
- `frontend/src/i18n/locales/ru.json`, `kk.json`, `en.json`: `certificates.listUnavailable`.
- `frontend/tests/certificates.test.mjs`: loading/error/retry/unavailable/empty и issued/revoked legacy cards.
- `frontend/tests/session-isolation.test.mjs`: protected certificate read after401 and same-account refresh.
- `certificates/test_profile_visibility.py`: пять isolated API-regressions; runtime backend не изменялся.
- Этот отчёт и `docs/project-memory/CURRENT_STATE.md`.

Все перечисленные прежде dirty файлы сохранены вместе с существующими изменениями; diff относительно HEAD содержит и более ранние фазы. Настройки, модели, миграции, eligibility и реальные записи не менялись.

## Реально выполненная верификация

- Django: `test certificates.test_profile_visibility certificates.tests certificates.test_admin` с in-memory DATABASES и temporary MEDIA_ROOT/PUBLIC_MEDIA_ROOT, заданными до setup: **44 passed,0failed**. Проверены owned legacy snapshot без name confirmation/активной policy, другая учётная запись/empty, revoked display/download denial, anonymous denial, global-disabled404 с сохранением row. System check passed.
- Frontend direct `node --test-timeout=30000 tests/certificates.test.mjs`: **8 passed**.
- Frontend direct session file: **57 passed**. Новый адаптер сначала имитирует реальный401 на старый access, затем принимает только обновлённый access того же аккаунта; refresh ровно один. Никаких реальных JWT/accounts/API не использовалось.
- `node --test --test-concurrency=2 --test-timeout=30000 tests/*.test.mjs`: **35files passed,0failed**, log `/tmp/p1f-frontend-tests.log`.
- `npm run lint`, `npm run build`, `git diff --check`: passed.
- Playwright MCP browser_tabs попытка: отсутствует настроенный Firefox executable. Ничего не устанавливалось; actual authenticated Profile/Network/JWT response в пользовательском браузере **NOT TESTED**. Автоматизированные результаты не подтверждают активный аккаунт или реально запущенный server process settings; runtime flag установлен из текущих project settings в диагностическом процессе.

## Оставшиеся шаги перед checkpoint

1. В существующей пользовательской сессии самостоятельно проверить account identity и Network `/api/my/certificates/` (status/body), не копируя токены. Ожидается404 при текущем gate; после UI-update должно быть unavailable, а не «сертификатов нет».
2. Решение о разделении чтения существующих сертификатов и отключения новой выдачи — отдельный scoped task. Не менять текущие policies/issuer или Certificate ради UI.
3. Дополнить будущий staging allowlist новыми тестом/отчётом P1F; старый P1E список — датированный снимок, не blanket authorization. Backup остаётся ignored и не должен попасть в Git.
4. Реальное браузерное подтверждение ownership/display остаётся открытым. Course10 unpublished, Course8 content и все сертификаты сохранены; повторная выдача/отзыв/удаление не выполнялись.
