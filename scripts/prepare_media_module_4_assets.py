"""Create only original local teaching assets; never connect to Django/SQLite."""
import argparse
import io
import json
import re
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def srt_example():
    content = json.loads((ROOT / 'courses/management/media_module_4.json').read_text(encoding='utf-8'))
    blocks = content['lessons'][1]['text_content'].split('\n\n')
    cues = [b for b in blocks if re.match(r'^\d+\n\d{2}:\d{2}:\d{2},\d{3} --> ', b)]
    if len(cues) != 3:
        raise ValueError('Expected three authored teaching SRT cues.')
    return ('\n\n'.join(cues) + '\n').encode('utf-8')


def workflow_png():
    # Original diagram drawn from text/shapes, not a product screenshot or AI
    # output. DejaVu Sans from the existing system supplies Cyrillic glyphs.
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    title = ImageFont.truetype(font_path, 42)
    heading = ImageFont.truetype(font_path, 28)
    body = ImageFont.truetype(font_path, 24)
    image = Image.new('RGB', (1600, 900), '#16181c')
    draw = ImageDraw.Draw(image)
    draw.text((70, 40), 'Ф1: путь от проверенного текста к аудиоэкспорту', font=title, fill='#f4f5f7')
    draw.text((70, 110), 'Вымышленный учебный проект. Схема процесса, не запись и не интерфейс CapCut.', font=body, fill='#c4c7d0')
    cards = [
        ('1. Текст и разрешения', 'Проверить факты. Выбрать согласованный голос.'),
        ('2. Оригинал', 'Записать или синтезировать. Сохранить без изменений.'),
        ('3. Рабочая копия', 'Применить только нужную обработку. Сравнить с оригиналом.'),
        ('4. Субтитры', 'Исправить слова. Выровнять по реальному аудио.'),
        ('5. Монтаж', 'Согласовать речь, кадры и разрешённую музыку.'),
        ('6. Проверка экспорта', 'Прослушать итоговый файл. Сохранить версию и происхождение.'),
    ]
    for i, (label, explanation) in enumerate(cards):
        x = 70 + (i % 3) * 510
        y = 200 + (i // 3) * 300
        draw.rounded_rectangle((x, y, x+450, y+230), radius=18, fill='#282c34', outline='#b594e5', width=3)
        draw.text((x+20, y+22), label, font=heading, fill='#f4f5f7')
        for line, value in enumerate(textwrap.wrap(explanation, width=29)):
            draw.text((x+20, y+80+line*34), value, font=body, fill='#f4f5f7')
        if i % 3 < 2:
            cy = y+115
            draw.line((x+458, cy, x+495, cy), fill='#b594e5', width=4)
            draw.polygon([(x+500,cy),(x+486,cy-9),(x+486,cy+9)],fill='#b594e5')
    # Explicit continuation between rows; numbering remains the text equivalent.
    draw.text((70, 450), 'Продолжение: после шага 3 переходите к шагу 4.', font=body, fill='#c4c7d0')
    draw.text((70, 810), 'Качество оценивают по разборчивости и смыслу. Обработка не заменяет исходник.', font=body, fill='#c4c7d0')
    output = io.BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()


def create_assets(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    files = {'m4-l2-f1-example.srt': srt_example(), 'm4-l3-audio-workflow.png': workflow_png()}
    for name, data in files.items():
        target = output / name
        if target.exists():
            if target.read_bytes() != data:
                raise ValueError(f'Existing asset conflicts: {target}')
        else:
            with target.open('xb') as destination:
                destination.write(data)
    return list(files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'course_assets/module_4')
    args = parser.parse_args()
    for name in create_assets(args.output_dir):
        print(args.output_dir / name)
