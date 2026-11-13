"""Verifier rejects corrupted/missing media and malformed subtitles."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from verify import verify_hash, verify_vtt, verify_video


class VerificationTests(unittest.TestCase):
    def test_valid_cues(self):
        self.assertEqual(verify_vtt('WEBVTT\n\n00:00:00.100 --> 00:00:01.000\nТекст\n', 2), 1)

    def test_invalid_cues(self):
        for text in ('', 'WEBVTT\n', 'WEBVTT\n00:00:00.000 --> broken\nТекст', 'WEBVTT\n00:00:00.000 --> 00:00:03.000\nТекст'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                verify_vtt(text, 2)

    def test_overlapping_cues(self):
        with self.assertRaises(ValueError):
            verify_vtt('WEBVTT\n00:00:00.000 --> 00:00:01.500\nА\n\n00:00:01.000 --> 00:00:02.000\nБ', 3)

    def test_missing_and_changed_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'asset'
            with self.assertRaises(ValueError):
                verify_hash(path, '0' * 64)
            path.write_bytes(b'approved')
            verify_hash(path, hashlib.sha256(b'approved').hexdigest())
            with self.assertRaises(ValueError):
                verify_hash(path, '0' * 64)

    def test_video_profile(self):
        asset = {'duration_frames': 60, 'duration_seconds': 2}
        video = dict(codec_type='video', codec_name='h264', width=1920, height=1080, pix_fmt='yuv420p', avg_frame_rate='30/1', nb_frames='60', duration='2')
        audio = dict(codec_type='audio', codec_name='aac', sample_rate='48000', channels=2, duration='2')
        verify_video({'streams': [video, audio]}, asset)
        for field, value in [('width', 1280), ('nb_frames', '59'), ('avg_frame_rate', '24/1')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify_video({'streams': [{**video, field: value}, audio]}, asset)


if __name__ == '__main__':
    unittest.main()
