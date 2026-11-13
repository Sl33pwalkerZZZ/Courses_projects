"""Mix sentence-level Silero narration with original procedural cues; no music."""
from array import array
import hashlib
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RATE, FPS = 48000, 30
SAMPLES_PER_FRAME = RATE // FPS
SOURCE = json.loads((ROOT / "content/videos.json").read_text(encoding="utf-8"))
VOICE_SOURCE = json.loads((ROOT / "content/narration-sentence-cues-provenance.json").read_text(encoding="utf-8"))
VOICE_CUES = {entry["video"]: {scene["scene"]: scene["cues"] for scene in entry["scenes"]} for entry in VOICE_SOURCE["videos"]}
EFFECTS = {
    "m5-l15-v1-export-check": [(0, "select"), (1, "place"), (2, "select"), (3, "place"), (4, "select"), (5, "finish")],
    "m5-l15-v2-vertical-adaptation": [(0, "select"), (1, "place"), (2, "place"), (3, "select"), (4, "place"), (5, "finish")],
    "m5-l15-v3-final-review": [(0, "select"), (1, "place"), (2, "select"), (3, "place"), (4, "select"), (5, "finish")],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_stereo(path: Path) -> array:
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-map", "0:a:0", "-ar", str(RATE), "-ac", "2", "-f", "f32le", "-"])
    values = array("f")
    values.frombytes(raw)
    if sys.byteorder != "little":
        values.byteswap()
    if not values or len(values) % 2:
        raise ValueError(f"Invalid audio decode: {path}")
    return values


def read_effect(path: Path) -> list[float]:
    metadata = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate,channels", "-of", "json", str(path)], text=True))
    stream = metadata.get("streams", [{}])[0]
    if (int(stream.get("sample_rate", 0)), int(stream.get("channels", 0))) != (RATE, 2):
        raise ValueError(f"Unexpected SFX format: {path}")
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-map", "0:a:0", "-ar", str(RATE), "-ac", "1", "-f", "f32le", "-"])
    samples = array("f")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    return list(samples)


def write_stereo(path: Path, samples: array) -> None:
    pcm = array("h", (round(max(-0.999, min(0.999, value)) * 32767) for value in samples))
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(path), "wb") as output:
        output.setparams((2, 2, RATE, 0, "NONE", "not compressed"))
        output.writeframes(pcm.tobytes())


def stamp(sample: int) -> str:
    millis = sample * 1000 // RATE
    seconds, millis = divmod(millis, 1000)
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"


def main() -> None:
    timing_path = ROOT / "content/timings-sentence.json"
    provenance_path = ROOT / "content/audio-sentence-mix-provenance.json"
    output_dir = ROOT / "out/audio-sentence"
    sfx_dir = ROOT / "public/sfx"
    targets = [timing_path, provenance_path]
    for video in SOURCE:
        stem = video["filename"]
        targets.extend([output_dir / f"{stem}-{suffix}.wav" for suffix in ("mix", "voice", "sfx")])
        targets.extend([ROOT / "out/final-sentence" / f"{stem}.{suffix}" for suffix in ("vtt", "ru.md")])
    if any(path.exists() for path in targets):
        raise SystemExit("Refusing to overwrite an existing audio, VTT, transcript, timing or provenance output.")

    for video in SOURCE:
        if set(VOICE_CUES[video["id"]]) != set(range(1, len(video["scenes"]) + 1)):
            raise SystemExit(f"Narration scene mapping is incomplete: {video['id']}")
        for scene_index, scene in enumerate(video["scenes"], 1):
            cues = VOICE_CUES[video["id"]][scene_index]
            if not cues or " ".join(cue["text"] for cue in cues) == "":
                raise SystemExit(f"Empty narration cues: {video['id']} scene {scene_index}")
            for cue in cues:
                path = ROOT / cue["path"]
                if not path.is_file() or sha(path) != cue["sha256"]:
                    raise SystemExit(f"Missing or changed narration cue: {cue['path']}")

    output_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "out/final-sentence").mkdir(parents=True, exist_ok=True)
    effects = {name: read_effect(sfx_dir / f"{name}.wav") for name in ("select", "place", "finish")}
    layouts, reports = {}, []
    for video in SOURCE:
        voice_peak = 0.0
        decoded_scenes = []
        for scene_index, _scene in enumerate(video["scenes"], 1):
            cues = []
            for cue in VOICE_CUES[video["id"]][scene_index]:
                path = ROOT / cue["path"]
                decoded = decode_stereo(path)
                voice_peak = max(voice_peak, max(abs(value) for value in decoded))
                cues.append((cue, path, decoded))
            decoded_scenes.append(cues)
        if voice_peak <= 0:
            raise ValueError(f"Silent speech: {video['id']}")
        voice_gain = min(1.0, 0.67 / voice_peak)
        cursor_frame = 0
        scene_layout, scheduled, cue_rows = [], [], []
        for scene_index, (scene, cues) in enumerate(zip(video["scenes"], decoded_scenes)):
            start_frame = cursor_frame
            start_sample = start_frame * SAMPLES_PER_FRAME
            speech_cursor = start_sample + round(0.55 * RATE)
            captions = []
            for cue, path, decoded in cues:
                start = speech_cursor
                end = start + len(decoded) // 2
                scheduled.append((start, decoded))
                cue_rows.append((start, end, cue["text"], path))
                captions.append({
                    "startFrame": round((start - start_sample) / SAMPLES_PER_FRAME),
                    "durationFrames": math.ceil((end - start) / SAMPLES_PER_FRAME),
                    "text": cue["text"],
                })
                speech_cursor = end + round(0.42 * RATE)
            if cues:
                speech_cursor -= round(0.42 * RATE)
            minimum_end = max(start_sample + 9 * RATE, speech_cursor + round(1.1 * RATE))
            scene_frames = max(9 * FPS, math.ceil((minimum_end - start_sample) / SAMPLES_PER_FRAME))
            scene_layout.append({
                "kind": scene["kind"], "startFrame": start_frame, "durationFrames": scene_frames,
                "startSample": start_sample, "endSample": (start_frame + scene_frames) * SAMPLES_PER_FRAME,
                "captions": captions, "voice_segments": [str(path.relative_to(ROOT)) for _, path, _ in cues],
            })
            cursor_frame += scene_frames

        total_samples = cursor_frame * SAMPLES_PER_FRAME
        voice_stem = array("f", [0.0]) * (total_samples * 2)
        sfx_stem = array("f", [0.0]) * (total_samples * 2)
        for start, decoded in scheduled:
            offset = start * 2
            for index, value in enumerate(decoded):
                voice_stem[offset + index] += value * voice_gain

        event_rows = []
        for scene_index, name in EFFECTS[video["id"]]:
            scene = scene_layout[scene_index]
            cue_sample = scene["startSample"] + round(2.15 * RATE)
            samples = effects[name]
            if cue_sample + len(samples) >= total_samples:
                cue_sample = max(scene["startSample"], total_samples - len(samples) - 1)
            gain = 0.8
            for index, value in enumerate(samples):
                sfx_stem[2 * (cue_sample + index)] += value * gain
                sfx_stem[2 * (cue_sample + index) + 1] += value * gain
            source_path = sfx_dir / f"{name}.wav"
            event_rows.append({"sample": cue_sample, "seconds": round(cue_sample / RATE, 3), "name": name, "gain": gain, "source": str(source_path.relative_to(ROOT)), "source_sha256": sha(source_path)})

        mix = array("f", (voice_stem[i] + sfx_stem[i] for i in range(len(voice_stem))))
        peak = max(abs(value) for value in mix)
        if not 0 < peak < 0.9:
            raise ValueError(f"Mixed audio peak outside safety range for {video['id']}: {peak}")
        mix_path = output_dir / f"{video['filename']}-mix.wav"
        voice_path = output_dir / f"{video['filename']}-voice.wav"
        sfx_path = output_dir / f"{video['filename']}-sfx.wav"
        write_stereo(mix_path, mix)
        write_stereo(voice_path, voice_stem)
        write_stereo(sfx_path, sfx_stem)

        vtt_path = ROOT / "out/final-sentence" / f"{video['filename']}.vtt"
        vtt_lines = ["WEBVTT", ""]
        for cue_index, (start, end, text, _path) in enumerate(cue_rows, 1):
            vtt_lines.extend([str(cue_index), f"{stamp(start)} --> {stamp(end)}", text.replace("`", ""), ""])
        vtt_path.write_text("\n".join(vtt_lines), encoding="utf-8")
        transcript_path = ROOT / "out/final-sentence" / f"{video['filename']}.ru.md"
        transcript_path.write_text(
            f"# {video['title']}\n\nУрок 115 · Ф1 — вымышленный учебный проект. Интерфейсы в видео — пояснительные схемы, не запись CapCut.\n\n" +
            "\n\n".join(scene["narration"].replace("`", "") for scene in video["scenes"]) + "\n",
            encoding="utf-8",
        )
        layouts[video["id"]] = {"durationFrames": cursor_frame, "durationSeconds": cursor_frame / FPS, "scenes": scene_layout}
        reports.append({
            "video": video["id"], "duration_frames": cursor_frame, "duration_seconds": cursor_frame / FPS,
            "sample_rate": RATE, "channels": 2, "voice_gain_db": round(20 * math.log10(voice_gain), 3),
            "mixed_sample_peak_dbfs": round(20 * math.log10(peak), 3),
            "voice_segments": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for cues in decoded_scenes for _, path, _ in cues],
            "voice_cues": [{"start": stamp(start), "end": stamp(end), "text": text, "source": str(path.relative_to(ROOT))} for start, end, text, path in cue_rows],
            "sfx_events": event_rows,
            "mix_path": str(mix_path.relative_to(ROOT)), "mix_sha256": sha(mix_path),
            "voice_stem": str(voice_path.relative_to(ROOT)), "voice_stem_sha256": sha(voice_path),
            "sfx_stem": str(sfx_path.relative_to(ROOT)), "sfx_stem_sha256": sha(sfx_path),
            "vtt_path": str(vtt_path.relative_to(ROOT)), "vtt_sha256": sha(vtt_path),
            "transcript_path": str(transcript_path.relative_to(ROOT)), "transcript_sha256": sha(transcript_path),
        })

    timing_path.write_text(json.dumps(layouts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    provenance_path.write_text(json.dumps({
        "status": "local_production_candidates_not_yet_author_approved",
        "music": "None; no continuous bed, loop or stretch.",
        "voice": "Silero v5_cis_base_nostress ru_roman; exact checkpoint and MIT provenance in content/narration-sentence-cues-provenance.json; notice in audio/LICENSE_CIS.",
        "mix": "PCM 48 kHz stereo. Sentence clips resampled from 24 kHz mono by FFmpeg; fixed per-video gain to peak-bound narration; original procedural Lesson 113 select/place/finish SFX copied and checksum recorded. No normalizer, compressor, music or application audio.",
        "subtitles": "WebVTT cues use actual sentence WAV sample boundaries plus their exact spoken text. Segment-aligned, not phoneme-level forced alignment.",
        "outputs": reports,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "videos": [{"id": row["video"], "seconds": row["duration_seconds"], "peak_dbfs": row["mixed_sample_peak_dbfs"], "vtt": row["vtt_path"], "cues": len(row["voice_cues"])} for row in reports]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
