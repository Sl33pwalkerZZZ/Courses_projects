"""Dry-run by default. A future approved run changes only Lesson 91.text_content."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / 'docs/courses/lesson91-content-edit-proposal.json'


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def load_proposal():
    proposal = json.loads(PROPOSAL.read_text())
    assert (proposal['course_id'], proposal['lesson_id'], proposal['field']) == (8, 91, 'text_content')
    assert sha(proposal['before']) == proposal['before_sha256']
    assert sha(proposal['after']) == proposal['after_sha256']
    assert proposal['before'].endswith(proposal['after'])
    assert proposal['after'].startswith('1.1. Что такое искусственный интеллект\n\n')
    assert len(proposal['removed_title_page_and_course_introduction']) == 7
    assert hashlib.sha256((ROOT / proposal['source']).read_bytes()).hexdigest() == proposal['source_sha256']
    return proposal


def read_only(path):
    connection = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    return connection


def integrity(connection):
    assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert not connection.execute('PRAGMA foreign_key_check').fetchall()


def current_body(connection):
    row = connection.execute('SELECT l.text_content,c.is_published FROM courses_lesson l '
        'JOIN courses_module m ON m.id=l.module_id JOIN courses_course c ON c.id=m.course_id '
        'WHERE l.id=91 AND c.id=8').fetchone()
    if row is None or row[1] != 1:
        raise ValueError('Expected published course 8 and lesson 91 membership')
    return row[0]


def classify(body, proposal):
    if body == proposal['after']:
        return 'already_applied'
    if body != proposal['before']:
        raise ValueError('Unexpected lesson text; refusing to overwrite teacher changes')
    return 'ready'


def snapshot(connection, mask_target=False):
    result = {}
    for (table,) in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        cursor = connection.execute('SELECT * FROM "' + table.replace('"', '""') + '"')
        columns = [item[0] for item in cursor.description]
        rows = []
        for source_row in cursor:
            row = list(source_row)
            if mask_target and table == 'courses_lesson' and row[columns.index('id')] == 91:
                row[columns.index('text_content')] = '__APPROVED_FIELD__'
            rows.append(json.dumps(row, ensure_ascii=False, default=lambda value: value.hex()))
        result[table] = (len(rows), sha('\n'.join(sorted(rows))))
    schema = list(connection.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name'))
    result['__schema__'] = sha(json.dumps(schema))
    return result


def apply_approved(database, backup, backup_sha256, approval_sha256, proposal):
    if approval_sha256 != proposal['after_sha256']:
        raise ValueError('Explicit approval checksum required')
    with read_only(database) as connection:
        if classify(current_body(connection), proposal) == 'already_applied':
            return 'already_applied'
    if not backup or hashlib.sha256(Path(backup).read_bytes()).hexdigest() != backup_sha256:
        raise ValueError('Verified backup checksum required')
    previous = read_only(backup)
    integrity(previous)
    if current_body(previous) != proposal['before']:
        raise ValueError('Backup does not contain the exact before state')
    baseline, protected = snapshot(previous), snapshot(previous, True)
    previous.close()
    connection = sqlite3.connect(database, timeout=15, isolation_level=None)
    try:
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('BEGIN IMMEDIATE')
        assert classify(current_body(connection), proposal) == 'ready'
        if snapshot(connection) != baseline:
            raise ValueError('Database changed after backup; prepare a fresh verified backup')
        changed = connection.execute('UPDATE courses_lesson SET text_content=? WHERE id=91 AND text_content=?',
            (proposal['after'], proposal['before']))
        assert changed.rowcount == 1
        assert current_body(connection) == proposal['after']
        assert snapshot(connection, True) == protected
        integrity(connection)
        connection.execute('COMMIT')
    except BaseException:
        if connection.in_transaction:
            connection.execute('ROLLBACK')
        raise
    finally:
        connection.close()
    return 'applied'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=ROOT / 'db.sqlite3')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--approval-sha256')
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--backup-sha256')
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error('Choose dry-run or apply')
    proposal = load_proposal()
    if args.apply:
        print(apply_approved(args.database, args.backup, args.backup_sha256, args.approval_sha256, proposal))
    else:
        with read_only(args.database) as connection:
            print('DRY RUN:', classify(current_body(connection), proposal), '— NO WRITE')
        print(''.join(difflib.unified_diff(proposal['before'].splitlines(True), proposal['after'].splitlines(True),
            fromfile='current/Lesson91.text_content', tofile='proposed/Lesson91.text_content')))


if __name__ == '__main__':
    main()
