"""Add the approved original ambient score under Lesson 115 narration/SFX.

Creates separate per-video audio stems for V1/V2/V3 and optionally muxes only
the V1 candidate. It never overwrites existing inputs or outputs.
"""
from array import array
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
FPS, RATE = 30, 48_000
BLOCK = RATE // 50  # 20 ms envelope resolution
TARGET_GAP_DB = 22.0
MAX_DUCK_DB = 6.0
ATTACK_SECONDS, RELEASE_SECONDS = 0.20, 1.00
VOICE_THRESHOLD_DBFS = -48.0
VIDEO_INPUTS = json.loads((ROOT / "content/videos.json").read_text(encoding="utf-8"))
TIMINGS = json.loads((ROOT / "content/timings-sentence.json").read_text(encoding="utf-8"))
MIX_REPORT = json.loads((ROOT / "content/audio-sentence-mix-provenance.json").read_text(encoding="utf-8"))
VOICE_REPORT = json.loads((ROOT / "content/narration-sentence-cues-provenance.json").read_text(encoding="utf-8"))
MUSIC_COPY = ROOT / "audio/music/minimal-tech-ambient-v1-theme-64s.wav"
MUSIC_ORIGINAL = REPO / "video-production/lesson-113-production/out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav"
COMPOSER = REPO / "video-production/lesson-113-production/scripts/prepare_music_preview.py"
OUTPUT = ROOT / "out/audio-bgm"
PROVENANCE = ROOT / "content/audio-bgm-provenance.json"
FINAL_MP4 = ROOT / "out/final-sentence/m5-l15-v1-bgm-candidate.mp4"
V1_MP4_SOURCE = ROOT / "out/final-sentence/m5-l15-v1-export-check.mp4"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_stereo(path: Path) -> array:
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-nostdin", "-i", str(path),
        "-map", "0:a:0", "-ar", str(RATE), "-ac", "2", "-f", "f32le", "-",
    ])
    samples = array("f")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    if not samples or len(samples) % 2:
        raise ValueError(f"Invalid stereo audio: {path}")
    return samples


def rms(values: array) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(x * x for x in values) / len(values))


def db(value: float) -> float:
    return 20 * math.log10(max(value, 1e-12))


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot compute median of an empty list")
    values = sorted(values)
    n = len(values)
    return values[n // 2] if n % 2 else (values[n // 2 - 1] + values[n // 2]) / 2


def cue_sample(timecode: str) -> int:
    hours, minutes, seconds = timecode.split(":")
    return round((int(hours) * 3600 + int(minutes) * 60 + float(seconds)) * RATE)


def write_pcm24(path: Path, samples: array) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    proc = subprocess.run([
        "ffmpeg", "-v", "error", "-nostdin", "-n", "-f", "f32le",
        "-ar", str(RATE), "-ac", "2", "-i", "pipe:0", "-c:a", "pcm_s24le", str(path),
    ], input=samples.tobytes(), check=False)
    if proc.returncode:
        raise RuntimeError(f"Could not write PCM24 WAV: {path}")


def load_composer():
    spec = importlib.util.spec_from_file_location("approved_ambient_composer", COMPOSER)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load existing score composer: {COMPOSER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate_music(path: Path, seconds: float, composer) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    left, right = composer.compose(seconds)
    expected = round(seconds * RATE)
    if len(left) != expected or len(right) != expected:
        raise ValueError(f"Composer duration mismatch: {len(left)} / {len(right)} samples; expected {expected}")
    composer.write_wav(path, left, right)


def cue_activity_mask(voice: array, cues: list[dict]) -> list[bool]:
    frames = len(voice) // 2
    blocks = (frames + BLOCK - 1) // BLOCK
    active = [False] * blocks
    for cue in cues:
        start = cue_sample(cue["start"])
        end = cue_sample(cue["end"])
        for block_index in range(max(0, start // BLOCK), min(blocks, (end + BLOCK - 1) // BLOCK)):
            a = block_index * BLOCK * 2
            b = min(frames, (block_index + 1) * BLOCK) * 2
            segment = voice[a:b]
            if db(rms(segment)) > VOICE_THRESHOLD_DBFS:
                active[block_index] = True
    return active


def music_gain_for_reference(voice: array, music: array, active: list[bool]) -> tuple[float, float, float]:
    frame_count = min(len(voice), len(music)) // 2
    voice_levels, music_levels = [], []
    for block_index, is_active in enumerate(active):
        if not is_active:
            continue
        a = block_index * BLOCK * 2
        b = min(frame_count, (block_index + 1) * BLOCK) * 2
        voice_levels.append(db(rms(voice[a:b])))
        music_levels.append(db(rms(music[a:b])))
    voice_median, music_median = median(voice_levels), median(music_levels)
    gain_db = voice_median - TARGET_GAP_DB - music_median
    if not -60 <= gain_db <= 0:
        raise ValueError(f"Unsafe calculated music gain: {gain_db:.2f} dB")
    return gain_db, voice_median, music_median


def make_ducked_music(music: array, active: list[bool], gain_db: float) -> tuple[array, float]:
    out = array("f", [0.0]) * len(music)
    attenuation_db = 0.0
    max_attenuation = 0.0
    step = BLOCK / RATE
    for block_index, start in enumerate(range(0, len(music), BLOCK * 2)):
        target = MAX_DUCK_DB if block_index < len(active) and active[block_index] else 0.0
        tau = ATTACK_SECONDS if target > attenuation_db else RELEASE_SECONDS
        attenuation_db += (target - attenuation_db) * (1 - math.exp(-step / tau))
        max_attenuation = max(max_attenuation, attenuation_db)
        gain = 10 ** ((gain_db - attenuation_db) / 20)
        end = min(len(music), start + BLOCK * 2)
        for index in range(start, end):
            out[index] = music[index] * gain
    return out, max_attenuation


def timeline_summary(voice: array, music: array, active: list[bool]) -> dict:
    levels = []
    frames = min(len(voice), len(music)) // 2
    for block_index, is_active in enumerate(active):
        if not is_active:
            continue
        a = block_index * BLOCK * 2
        b = min(frames, (block_index + 1) * BLOCK) * 2
        levels.append(db(rms(music[a:b])) - db(rms(voice[a:b])))
    return {
        "speech_active_blocks": sum(active),
        "music_to_voice_median_db_during_speech_after_duck": round(median(levels), 2),
        "music_to_voice_min_max_db_during_speech_after_duck": [round(min(levels), 2), round(max(levels), 2)],
    }


def main() -> None:
    if not MUSIC_ORIGINAL.is_file() or not MUSIC_COPY.is_file():
        raise FileNotFoundError("The original 64-second theme and its verified Lesson 115 copy are required.")
    original_music_hash = sha(MUSIC_ORIGINAL)
    if sha(MUSIC_COPY) != original_music_hash:
        raise ValueError("Copied music asset does not match the original source checksum.")
    if PROVENANCE.exists():
        raise FileExistsError(f"Refusing to overwrite {PROVENANCE}")
    if FINAL_MP4.exists():
        raise FileExistsError(f"Refusing to overwrite {FINAL_MP4}")

    source_video_hash = sha(V1_MP4_SOURCE)
    composer = load_composer()
    source_script_hash = sha(COMPOSER)
    report = {
        "status": "local_candidate_pending_human_listening_and_author_approval",
        "track": {
            "title": "Minimal Tech Ambient — original AI Courses theme",
            "creator": "AI Courses project, procedurally synthesized",
            "local_source_asset": str(MUSIC_COPY.relative_to(ROOT)),
            "original_source_asset": str(MUSIC_ORIGINAL.relative_to(REPO)),
            "source_sha256": original_music_hash,
            "composer_source": str(COMPOSER.relative_to(REPO)),
            "composer_source_sha256": source_script_hash,
            "method": "Original deterministic Python standard-library additive synthesis with procedural filtered noise; no downloaded recordings, samples, lyrics, pretrained model or external music API.",
            "score": "72 BPM; Dmaj9 → Bm7 → Gmaj9 → Aadd9; sparse sine pads, original bell motif and soft pulse; same score continued at native tempo for each full video duration.",
            "license_and_use": "No third-party audio or third-party license terms are present. This project-created composition was previously approved by the course owner for the AI Courses video series. No broader sublicense or ownership claim is made here; confirm with the rights holder if use outside this project is planned.",
        },
        "configuration": {
            "music_reference_gap_db_below_active_narration": TARGET_GAP_DB,
            "duck_max_db": MAX_DUCK_DB,
            "duck_attack_seconds": ATTACK_SECONDS,
            "duck_release_seconds": RELEASE_SECONDS,
            "speech_activity_threshold_dbfs": VOICE_THRESHOLD_DBFS,
            "fade_in_seconds": 1.2,
            "fade_out_seconds": 2.0,
            "fade_method": "Existing composer raised-cosine gain envelope.",
            "looping_or_stretching": "None. The existing score generator composes each complete duration at native tempo; the harmonic phrase continues without a loop boundary.",
            "music_sample_rate_hz": RATE,
            "channels": 2,
            "music_pcm_format": "PCM signed 24-bit WAV",
            "sfx_and_narration": "Existing voice+SFX PCM16 mix is used unchanged as the foreground input; the separate voice stem only controls music ducking. No VTT timing is rewritten.",
            "processing": "Linear music gain and smooth duck envelope, additive float mix, PCM24 WAV output; no compressor, limiter or time stretch.",
        },
        "videos": [],
        "candidate_mp4": None,
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    for video in VIDEO_INPUTS:
        video_id, stem = video["id"], video["filename"]
        print(f"Processing {video_id}...", flush=True)
        layout = TIMINGS[video_id]
        expected_samples = round(layout["durationFrames"] / FPS * RATE)
        output_files = {
            "music_base": OUTPUT / f"{stem}-music-base.wav",
            "music_bed": OUTPUT / f"{stem}-music.wav",
            "mix": OUTPUT / f"{stem}-bgm-mix.wav",
        }
        existing = [path.exists() for path in output_files.values()]
        if any(existing) and not all(existing):
            raise FileExistsError(f"Incomplete pre-existing output set for {video_id}; refusing to overwrite or guess.")
        inputs = {
            "foreground_mix": ROOT / "out/audio-sentence" / f"{stem}-mix.wav",
            "voice_control": ROOT / "out/audio-sentence" / f"{stem}-voice.wav",
        }
        if not all(path.is_file() for path in inputs.values()):
            raise FileNotFoundError(f"Missing existing V1/V2/V3 audio input for {video_id}")
        voice_cues = next(x for x in MIX_REPORT["outputs"] if x["video"] == video_id)["voice_cues"]
        foreground = decode_stereo(inputs["foreground_mix"])
        voice = decode_stereo(inputs["voice_control"])
        if len(foreground) != expected_samples * 2 or len(voice) != expected_samples * 2:
            raise ValueError(f"Unexpected existing audio sample count for {video_id}")

        duration = layout["durationFrames"] / FPS
        if all(existing):
            # Resume safely after an interrupted batch: accept only a complete,
            # decodable trio with exact duration and valid mix headroom.
            base_music = decode_stereo(output_files["music_base"])
            music_bed = decode_stereo(output_files["music_bed"])
            saved_mix = decode_stereo(output_files["mix"])
            if any(len(x) != expected_samples * 2 for x in (base_music, music_bed, saved_mix)):
                raise ValueError(f"Existing output duration mismatch for {video_id}")
            saved_peak_dbfs = db(max(abs(x) for x in saved_mix))
            if saved_peak_dbfs > -1.5:
                raise ValueError(f"Existing mix exceeds safe headroom for {video_id}: {saved_peak_dbfs:.2f} dBFS")
            del saved_mix
        else:
            generate_music(output_files["music_base"], duration, composer)
            base_music = decode_stereo(output_files["music_base"])
        if len(base_music) != expected_samples * 2:
            raise ValueError(f"Music does not cover the exact duration of {video_id}")
        active = cue_activity_mask(voice, voice_cues)
        music_gain_db, voice_rms_db, music_rms_db = music_gain_for_reference(voice, base_music, active)
        if not all(existing):
            music_bed, max_duck = make_ducked_music(base_music, active, music_gain_db)
        else:
            expected_bed, max_duck = make_ducked_music(base_music, active, music_gain_db)
            # Existing files are accepted only if they correspond to the
            # declared settings; tolerate PCM24 quantization only.
            if len(expected_bed) != len(music_bed) or any(abs(a - b) > 2e-5 for a, b in zip(expected_bed, music_bed)):
                raise ValueError(f"Existing music bed does not match declared settings for {video_id}")
            del expected_bed
        music_rms_after = timeline_summary(voice, music_bed, active)
        mix = array("f", (foreground[i] + music_bed[i] for i in range(len(foreground))))
        if all(existing):
            peak_dbfs = db(max(abs(x) for x in decode_stereo(output_files["mix"])))
        else:
            peak_dbfs = db(max(abs(x) for x in mix))
        if peak_dbfs > -1.5:
            raise ValueError(f"Mix peak exceeds safe pre-encode headroom for {video_id}: {peak_dbfs:.2f} dBFS")
        if not all(existing):
            write_pcm24(output_files["music_bed"], music_bed)
            write_pcm24(output_files["mix"], mix)
        for path in output_files.values():
            subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-i", str(path), "-f", "null", "-"], check=True, capture_output=True)
        report["videos"].append({
            "id": video_id,
            "duration_seconds": duration,
            "active_narration_rms_median_dbfs": round(voice_rms_db, 2),
            "unattenuated_music_rms_median_in_speech_windows_dbfs": round(music_rms_db, 2),
            "music_gain_db": round(music_gain_db, 2),
            "baseline_music_gap_db": round(music_rms_db + music_gain_db - voice_rms_db, 2),
            "max_duck_reached_db": round(max_duck, 2),
            **music_rms_after,
            "mixed_sample_peak_dbfs": round(peak_dbfs, 2),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in inputs.items()},
            "outputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in output_files.items()},
            "vtt": {"path": f"out/final-sentence/{stem}.vtt", "sha256": sha(ROOT / "out/final-sentence" / f"{stem}.vtt")},
        })
        del foreground, voice, base_music, music_bed
        if not all(existing):
            del mix

    if sha(V1_MP4_SOURCE) != source_video_hash:
        raise AssertionError("Original V1 video changed during audio preparation.")
    v1_mix = ROOT / "out/audio-bgm/m5-l15-v1-export-check-bgm-mix.wav"
    command = [
        "ffmpeg", "-v", "error", "-nostdin", "-n", "-i", str(V1_MP4_SOURCE), "-i", str(v1_mix),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
        "-ar", str(RATE), "-ac", "2", "-shortest", "-movflags", "+faststart", str(FINAL_MP4),
    ]
    subprocess.run(command, check=True)
    report["candidate_mp4"] = {
        "path": str(FINAL_MP4.relative_to(ROOT)),
        "sha256": sha(FINAL_MP4),
        "original_v1_sha256_before_and_after": source_video_hash,
        "ffmpeg_command": command,
        "video_stream": "Copied from original V1 with -c:v copy; no Remotion render or video re-encode.",
    }
    PROVENANCE.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "candidate": report["candidate_mp4"],
        "videos": [{
            "id": x["id"], "seconds": x["duration_seconds"],
            "music_gain_db": x["music_gain_db"],
            "speech_music_gap_after_duck_db": x["music_to_voice_median_db_during_speech_after_duck"],
            "sample_peak_dbfs": x["mixed_sample_peak_dbfs"],
        } for x in report["videos"]],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
