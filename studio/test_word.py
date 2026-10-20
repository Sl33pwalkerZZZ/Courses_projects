"""Upload parsing uses in-memory fixtures, never actual course records."""
import io
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from zlib import error as ZlibError
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from .word import parse_docx


def docx(body, extra=None):
    output = io.BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>' + body + '</w:body></w:document>')
        for name, value in (extra or {}).items():
            archive.writestr(name, value)
    return output.getvalue()


def paragraph(text, style=""):
    return '<w:p>' + (f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else '') + f'<w:r><w:t>{escape(text)}</w:t></w:r></w:p>'


class WordPreviewTests(TestCase):
    def test_corrupt_compressed_streams_are_validation_errors(self):
        for error in (ZlibError('corrupt compressed stream'), EOFError('truncated member')):
            with self.subTest(error=type(error).__name__), patch('studio.word.ZipFile.read', side_effect=error):
                with self.assertRaisesRegex(ValueError, 'damaged or unsupported'):
                    parse_docx(docx(paragraph('Content')), 'source.docx')

    def test_preserves_headings_paragraphs_tables_and_safe_reference(self):
        body = paragraph('Перед началом') + paragraph('Раздел', 'Heading1') + paragraph('<script>plain text</script>')
        body += '<w:tbl><w:tr><w:tc>' + paragraph('Сервис') + '</w:tc><w:tc>' + paragraph('Цена') + '</w:tc></w:tr><w:tr><w:tc>' + paragraph('A') + '</w:tc><w:tc>' + paragraph('0') + '</w:tc></w:tr></w:tbl>'
        body += '<w:p><w:hyperlink r:id="link"><w:r><w:t>Reference</w:t></w:r></w:hyperlink></w:p>'
        relationships = '<Relationships><Relationship Id="link" Type="https://example.org/hyperlink" Target="https://example.org/reference"/></Relationships>'
        result = parse_docx(docx(body, {'word/_rels/document.xml.rels': relationships}), '../source.docx')
        self.assertEqual(result['source_name'], 'source.docx')
        self.assertEqual(result['title'], 'Раздел')
        self.assertEqual(len(result['lessons']), 1)
        self.assertIn('Перед началом', result['lessons'][0]['text_content'])
        self.assertIn('<script>plain text</script>', result['lessons'][0]['text_content'])
        self.assertEqual(result['blocks'][3]['headers'], ['Сервис', 'Цена'])
        self.assertIn('https://example.org/reference', result['lessons'][0]['text_content'])

    def test_no_heading_still_preserves_all_text(self):
        result = parse_docx(docx(paragraph('One') + paragraph('Two')), 'source.docx')
        self.assertEqual(result['lessons'][0]['text_content'], 'One\n\nTwo')

    def test_rejects_wrong_extension_and_corrupt_archive(self):
        for data, name in [(b'not zip', 'source.docx'), (docx(paragraph('x')), 'source.docm'), (b'', 'source.docx')]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                parse_docx(data, name)

    def test_rejects_traversal_macros_entities_and_expansion_bombs(self):
        cases = [
            docx(paragraph('x'), {'../evil': 'bad'}),
            docx(paragraph('x'), {'word/vbaProject.bin': 'bad'}),
            docx(paragraph('x'), {'word/huge.xml': ' ' * (31 * 1024 * 1024)}),
            docx(paragraph('x'), {'word/styles.xml': '<!DOCTYPE x [<!ENTITY a "bad">]><styles/>'}),
            docx(paragraph('x'), {'word/styles.xml': '<!DOCTYPE x [<!ENTITY a "bad">]><styles/>'.encode('utf-16')}),
        ]
        for index, data in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(ValueError):
                parse_docx(data, 'source.docx')

    def test_unsafe_links_omitted_and_embedded_media_warned(self):
        body = '<w:p><w:hyperlink r:id="link"><w:r><w:t>Unsafe reference</w:t></w:r></w:hyperlink></w:p>'
        relationships = '<Relationships><Relationship Id="link" Type="https://example.org/hyperlink" Target="javascript:alert(1)"/></Relationships>'
        result = parse_docx(docx(body, {'word/_rels/document.xml.rels': relationships, 'word/media/image.png': b'ignored'}), 'source.docx')
        self.assertNotIn('javascript:', result['lessons'][0]['text_content'])
        self.assertTrue(any('unsupported link' in warning for warning in result['warnings']))
        self.assertTrue(any('illustrations' in warning for warning in result['warnings']))

    def test_actual_chapter_can_be_previewed_without_writing(self):
        path = Path('course_sources/Глава_1_Выбор_ИИ_модели_и_сервиса.docx')
        if not path.exists():
            self.skipTest('Local private source is optional outside this environment.')
        before = path.stat()
        result = parse_docx(path.read_bytes(), path.name)
        self.assertEqual(sum(block['type'] == 'table' for block in result['blocks']), 4)
        self.assertTrue(any('1.8' in lesson['text_content'] for lesson in result['lessons']))
        self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
