"""Read-only Phase 5B source checks; no Django, DB, media generation or imports.

Run: python3 -B scripts/validate_media_module_5_sources.py
This validates consistency, not factual accuracy, licensing or completed media.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'Создание и монтаж видео в CapCut Desktop'
TITLES = [
    'Подготовка видеопроекта и организация материалов',
    'Монтаж, озвучка и интеллектуальные инструменты',
    'Экспорт, адаптация и подготовка видео к публикации',
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def validate():
    source = read('courses/management/media_module_5.json')
    boards = read('docs/courses/media-module-5-storyboards.json')
    manifest = read('docs/courses/media-module-5-assets.json')
    review = (ROOT / 'docs/courses/media-module-5-content-review.md').read_text(encoding='utf-8')
    require(set(source) == {'module', 'lessons'} and source['module'] == MODULE, 'Unexpected source schema/module')
    require([lesson['title'] for lesson in source['lessons']] == TITLES, 'Wrong lesson count/order/titles')
    summary = []
    for lesson in source['lessons']:
        require(set(lesson) == {'title', 'objectives', 'source_sections', 'text_content'}, 'Unexpected lesson fields')
        require(len(lesson['objectives']) == 3 and all(isinstance(s, str) and 0 < len(s) <= 1000 for s in lesson['objectives']), 'Need three bounded objectives')
        headings = lesson['source_sections']
        require(len(headings) == 9 and len(set(headings)) == 9 and all(0 < len(s) <= 255 for s in headings), 'Need nine unique bounded headings')
        paragraphs = lesson['text_content'].split('\n\n')
        positions = [paragraphs.index(h) for h in headings]
        require(positions[0] == 0 and positions == sorted(positions) and all(paragraphs.count(h) == 1 for h in headings), 'Headings must be exact ordered paragraphs')
        counts = []
        for index, start in enumerate(positions):
            stop = positions[index + 1] if index + 1 < len(positions) else len(paragraphs)
            count = len(' '.join(paragraphs[start+1:stop]).split())
            require(count >= 50, f'Section needs substantive review: {headings[index]}')
            counts.append(count)
        require('вымышлен' in lesson['text_content'] and 'Ф1' in lesson['text_content'], 'Missing explicit fictional case')
        require(headings[-1] == '9. Самостоятельная практика без оценки', 'Practice must be explicitly optional/ungraded')
        require('модул' in paragraphs[-1] and '6' in paragraphs[-1], 'Missing Module 6 assessment boundary')
        require(all(p in review for p in paragraphs) and all(o in review for o in lesson['objectives']), 'Reading copy differs from canonical source')
        summary.append(dict(title=lesson['title'], objectives=3, sections=9,
                            words=len(lesson['text_content'].split()), section_words=counts))

    for data in [boards, manifest]:
        require((data['course_id'], data['course_slug'], data['module_order'], data['module_title']) ==
                (10, 'ai-media-content', 5, MODULE), 'Target must be existing course 10/module 5')
    videos = boards['videos']
    require(len(videos) == 9 and len({v['key'] for v in videos}) == 9, 'Exactly nine unique storyboards required')
    for number in [13, 14, 15]:
        group = [v for v in videos if v['course_lesson'] == number]
        require(sorted(v['video_order'] for v in group) == [1, 2, 3], 'Need three ordered demonstrations per lesson')
        require(len({v['after_section'] for v in group}) == 3, 'One video per distinct anchor')
    for video in videos:
        lesson = source['lessons'][video['lesson_order']-1]
        require(video['course_lesson'] == video['lesson_order']+12 and video['lesson_title'] == lesson['title'], 'Lesson mapping conflict')
        require(video['after_section'] in lesson['source_sections'][:-2], 'Invalid instructional video anchor')
        require(video['status'] == 'planned_not_created', 'Unexpected recording approval')
        require(video['timing_status'] == 'planned_edit_timeline_not_measured_recording_or_caption_cues', 'Storyboard times must not claim real synchronization')
        previous = 0
        require(len(video['storyboard']) >= 4 and video['prerequisites_ru'] and video['human_review_ru'], 'Storyboard detail missing')
        for shot in video['storyboard']:
            require(type(shot['start_seconds']) is int and type(shot['end_seconds']) is int
                    and shot['start_seconds'] == previous < shot['end_seconds'], 'Gap/overlap in planned storyboard')
            previous = shot['end_seconds']
            for field in ['screen_ru', 'onscreen_actions_ru', 'narration_ru', 'verification_ru', 'pause_and_readability_ru']:
                require(isinstance(shot[field], str) and shot[field].strip(), 'Missing storyboard detail')
            require(all(shot[field] in review for field in ['screen_ru','onscreen_actions_ru','narration_ru','verification_ru']), 'Reading copy misses storyboard')
        require(previous == video['expected_duration_seconds'] and 60 <= previous <= 180, 'Expected short-demo duration mismatch')
        require(video['narration_script_ru'] == '\n\n'.join(s['narration_ru'] for s in video['storyboard']), 'Narration script differs from shot narration')

    assets = manifest['assets']
    require(len(assets) == 18 and len({a['filename'] for a in assets}) == 18, 'Need nine MP4s and nine planned VTTs')
    require(manifest['status'] == 'planning_only_no_files_created' and manifest['apply_blocked_reason'], 'Import must remain blocked')
    for video in videos:
        group = [a for a in assets if a['storyboard_key'] == video['key']]
        require(len(group) == 2 and {a['kind'] for a in group} == {'video', 'vtt'}, 'Missing video/track pair')
        for asset in group:
            require(asset['after_section'] == video['after_section'] and asset['lesson_order'] == video['lesson_order']
                    and asset['lesson_title'] == video['lesson_title'], 'Asset placement/mapping differs')
            extension = 'mp4' if asset['kind'] == 'video' else 'vtt'
            require(re.fullmatch(r'm5-l(?:13|14|15)-v[123]-[a-z0-9-]+\.'+extension, asset['filename']), 'Unstable/unsafe planned filename')
            require(asset['status'] == 'planned_not_created' and all(asset[field] is False for field in
                    ['human_review_approved', 'transcript_verified', 'distribution_permission_confirmed']), 'Unapproved media must not become importable')
            require(all(asset[field] is None for field in ['sha256', 'duration_seconds', 'recorded_app_version', 'recorded_os', 'actual_media_metadata']), 'Actual metadata must remain unknown until recording')
            require(asset['alternative_ru'] == video['narration_script_ru'], 'Planned text equivalent differs from script')
            require(not (ROOT / manifest['asset_directory'] / asset['filename']).exists(), 'Planned asset now exists: review provenance/status instead of pretending it is absent')
        recording = next(a for a in group if a['kind'] == 'video')
        track = next(a for a in group if a['kind'] == 'vtt')
        require(recording['filename'] == video['filename'] and track['filename'] == video['subtitle_filename']
                and track['matching_video_filename'] == recording['filename'] and track['language'] == 'ru', 'Subtitle relation conflict')
    return dict(status='PASS_SOURCE_CONSISTENCY_ONLY', course_id=10, module_order=5,
                lessons=summary, videos=9, storyboard_shots=sum(len(v['storyboard']) for v in videos),
                planned_vtt_tracks=9, actual_media_files=0,
                expected_demo_seconds=[v['expected_duration_seconds'] for v in videos],
                human_approval='PENDING', database_access=False)


if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
