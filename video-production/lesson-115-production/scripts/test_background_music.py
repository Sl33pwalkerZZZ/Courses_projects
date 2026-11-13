"""Small deterministic regression checks for music level and duck envelopes."""
import importlib.util
import math
from array import array
from pathlib import Path
import unittest

SCRIPT = Path(__file__).with_name("mix_background_music.py")
spec = importlib.util.spec_from_file_location("l115_music_mixer_test", SCRIPT)
mixer = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mixer)


class BackgroundMusicMixTests(unittest.TestCase):
    def test_gain_targets_music_reference_gap(self):
        voice = array("f", [0.1] * 4000)
        music = array("f", [0.1] * 4000)
        active = [True] * 100
        gain, voice_db, music_db = mixer.music_gain_for_reference(voice, music, active)
        self.assertAlmostEqual(music_db + gain - voice_db, -22.0, places=5)

    def test_duck_attack_and_release_are_smooth_and_bounded(self):
        block_count = 240  # 4.8 seconds
        active = [20 <= i < 120 for i in range(block_count)]
        music = array("f", [0.1] * (block_count * mixer.BLOCK * 2))
        ducked, max_attenuation = mixer.make_ducked_music(music, active, 0.0)
        rms_at = lambda b: mixer.rms(ducked[b * mixer.BLOCK * 2:(b + 1) * mixer.BLOCK * 2])
        self.assertGreater(rms_at(22), rms_at(70))  # attack into speech
        self.assertLess(rms_at(130), rms_at(230))  # release is gradual, not abrupt
        self.assertGreaterEqual(max_attenuation, 5.9)
        self.assertLessEqual(max_attenuation, mixer.MAX_DUCK_DB)

    def test_activity_gate_uses_voice_level_in_requested_cues(self):
        voice = array("f", [0.0] * (mixer.RATE * 2))
        for i in range(20_000, 40_000):
            voice[2 * i] = voice[2 * i + 1] = 0.2
        active = mixer.cue_activity_mask(voice, [{"start": "00:00:00.400", "end": "00:00:00.800"}])
        self.assertTrue(any(active[20:40]))
        self.assertFalse(any(active[:10]))
        self.assertFalse(any(active[45:]))

    def test_envelope_helper_has_no_nonfinite_samples(self):
        samples = array("f", [0.1] * (80 * mixer.BLOCK * 2))
        active = [False] * 80
        _, _ = mixer.make_ducked_music(samples, active, -6.0)
        self.assertTrue(math.isfinite(mixer.db(mixer.rms(samples))))


if __name__ == "__main__":
    unittest.main()
