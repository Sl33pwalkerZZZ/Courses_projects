"""Final approved assets: inspection only; never generate speech or filter audio."""
from array import array
import hashlib
import json
from pathlib import Path
import sys
import wave

from django.conf import settings
from django.test import SimpleTestCase
from courses.attachments import validate_file
from courses.management.commands.import_lesson_media import load_assets


class FinalModule4AssetsTests(SimpleTestCase):
    def setUp(self):
        self.root=Path(settings.BASE_DIR)
        self.assets=self.root/'course_assets/module_4'
        self.manifest=self.root/'docs/courses/media-module-4-assets.json'
        self.data=json.loads(self.manifest.read_text())
        self.provenance=json.loads((self.root/'docs/courses/module-4-final-provenance.json').read_text())

    def test_four_author_selected_sources_are_byte_identical_and_complete(self):
        self.assertEqual(len(self.provenance['audio']),4)
        for name,meta in self.provenance['audio'].items():
            with self.subTest(filename=name):
                raw=(self.assets/name).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),meta['sha256'])
                self.assertEqual(validate_file(name,raw),('audio','audio/wav'))
                with wave.open(str(self.assets/name),'rb') as wav:
                    self.assertEqual((wav.getframerate(),wav.getnchannels(),wav.getsampwidth()),(24000,1,2))
                    self.assertEqual(wav.getnframes()/24000,meta['duration_seconds'])
                    pcm=array('h',wav.readframes(wav.getnframes()))
                    if sys.byteorder!='little':pcm.byteswap()
                    self.assertGreater(max(map(abs,pcm)),1000)
                    self.assertLess(max(map(abs,pcm)),32767)

    def test_seven_final_assets_all_approved_inline_and_mit_attributed(self):
        data,ready,skipped=load_assets(self.manifest,self.assets)
        self.assertEqual(len(ready),7);self.assertFalse(skipped)
        self.assertEqual([e['lesson_order'] for e,_ in ready],[1,2,2,2,3,3,3])
        for entry,_ in ready:
            self.assertTrue(entry['after_section'])
            self.assertNotIn('ElevenLabs',entry['caption_ru'])
            self.assertNotIn('eSpeak',entry['provenance'])
            if entry['kind']=='audio':
                self.assertEqual(entry['status'],'approved');self.assertTrue(entry['human_review_approved'])
                self.assertIn('MIT License',entry['provenance'])
                self.assertEqual(entry['license']['spdx'],'MIT')
        after=next(e for e in data['assets'] if e['key']=='processing-comparison-filtered')
        self.assertIn('DSP',after['caption_ru'])
        self.assertIn('не нейросетевой алгоритм',after['caption_ru'].casefold())
        self.assertEqual(self.provenance['lesson12_output_sha256'],after['sha256'])

    def test_subtitles_exact_approved_audio_segment_offsets_and_transcript(self):
        report=self.provenance
        speech=next(e for e in self.data['assets'] if e['key']=='stt-demonstration')
        srt=next(e for e in self.data['assets'] if e['key']=='srt-synchronized')
        self.assertEqual(hashlib.sha256((self.assets/srt['filename']).read_bytes()).hexdigest(),srt['sha256'])
        with wave.open(str(self.assets/speech['filename']),'rb') as wav:
            raw=wav.readframes(wav.getnframes())
        for cue in report['lesson11_cues']:
            segment=raw[cue['start_sample']*2:cue['end_sample']*2]
            self.assertEqual(hashlib.sha256(segment).hexdigest(),cue['segment_pcm_sha256'])
        self.assertEqual(speech['alternative_ru'],' '.join(c['text'] for c in report['lesson11_cues']))
        self.assertEqual(srt['matching_audio_filename'],speech['filename'])
