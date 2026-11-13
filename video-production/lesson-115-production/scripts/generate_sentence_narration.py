"""Synthesize sentence-level Lesson 115 speech cues with the existing local Silero checkpoint."""
from array import array
import argparse
import hashlib
import json
import math
import resource
import sys
import time
import unicodedata
import wave
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "v5_cis_base_nostress"
MODEL_SHA256 = "0405777e332906f0644e08a680f7cfdc2137ea864090079c1fdd30a43c1b8761"
MODEL_URL = "https://models.silero.ai/models/tts/ru/v5_cis_base_nostress.pt"
LICENSE_URL = "https://github.com/snakers4/silero-models/blob/master/LICENSE_CIS"
SPEAKER = "ru_roman"
RATE = 24000


def split_sentences(value: str) -> list[str]:
    import re
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", value.strip()) if part.strip()]


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.replace("+", "").replace("`", ""))
    return " ".join(unicodedata.normalize("NFC", "".join(c for c in decomposed if unicodedata.category(c) != "Mn")).split())


def model_stress(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    out: list[str] = []
    for char in decomposed:
        if char == "\u0301":
            if not out or out[-1] not in "аеёиоуыэюяАЕЁИОУЫЭЮЯ":
                raise ValueError("Stress mark is not attached to a Russian vowel.")
            vowel = out.pop()
            out.extend(("+", vowel))
        else:
            out.append(char)
    return unicodedata.normalize("NFC", "".join(out))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_wav(path: Path, pcm: array) -> None:
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        output.writeframes(pcm.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    if not args.checkpoint.is_file() or sha(args.checkpoint.read_bytes()) != MODEL_SHA256:
        raise SystemExit("Checkpoint is absent or its verified SHA-256 does not match.")
    videos = json.loads((ROOT / "content/videos.json").read_text(encoding="utf-8"))
    audio_dir = ROOT / "audio/narration_sentences"
    report_path = ROOT / "content/narration-sentence-cues-provenance.json"
    if report_path.exists():
        raise SystemExit("Refusing to overwrite existing sentence-cue provenance.")
    rows = []
    for video in videos:
        for index, scene in enumerate(video["scenes"], 1):
            plain = split_sentences(scene["narration"])
            marked = split_sentences(scene["synthesis"])
            if len(plain) != len(marked) or any(normalize(a) != normalize(b) for a, b in zip(plain, marked)):
                raise SystemExit(f"Sentence/stress mismatch: {video['id']} scene {index}")
            for cue_index in range(1, len(plain) + 1):
                path = audio_dir / video["id"] / f"scene-{index:02}-cue-{cue_index:02}.wav"
                if path.exists():
                    raise SystemExit(f"Refusing to overwrite narration cue: {path}")
                rows.append((video, index, cue_index, plain[cue_index - 1], marked[cue_index - 1], path))
    audio_dir.mkdir(parents=True, exist_ok=True)
    import torch
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    model = torch.package.PackageImporter(str(args.checkpoint)).load_pickle("tts_models", "model")
    model.to(torch.device("cpu"))
    if SPEAKER not in model.speakers:
        raise SystemExit("Required Russian speaker ru_roman is missing from the checkpoint.")

    generated: dict[tuple[str, int], list[dict]] = {}
    started = time.monotonic()
    for video, scene_index, cue_index, plain, readable_stress, path in rows:
        ssml_text = model_stress(readable_stress)
        ssml = f'<speak><prosody rate="94%">{escape(ssml_text)}</prosody></speak>'
        with torch.inference_mode():
            audio = model.apply_tts(ssml_text=ssml, speaker=SPEAKER, sample_rate=RATE).detach().cpu().flatten()
        if not bool(torch.isfinite(audio).all()) or audio.numel() < RATE // 4:
            raise SystemExit(f"Invalid/short synthesis: {video['id']} scene {scene_index} cue {cue_index}")
        peak = float(audio.abs().max())
        if not 0 < peak < 1:
            raise SystemExit(f"Silent/clipped synthesis: {video['id']} scene {scene_index} cue {cue_index}")
        pcm = array("h", (round(float(value) * 32767) for value in audio.tolist()))
        path.parent.mkdir(parents=True, exist_ok=True)
        write_wav(path, pcm)
        row = {
            "scene": scene_index, "cue": cue_index, "text": plain,
            "synthesis_input": readable_stress, "model_input": ssml_text,
            "ssml": ssml, "path": str(path.relative_to(ROOT)),
            "samples": len(pcm), "duration_seconds": len(pcm) / RATE,
            "sha256": sha(path.read_bytes()), "peak_dbfs": round(20 * math.log10(peak), 3),
        }
        generated.setdefault((video["id"], scene_index), []).append(row)

    output = []
    for video in videos:
        output.append({
            "video": video["id"],
            "scenes": [{"scene": index, "cues": generated[(video["id"], index)]} for index in range(1, len(video["scenes"]) + 1)],
        })
    report_path.write_text(json.dumps({
        "status": "generated_candidates_pending_human_voice_review",
        "model_id": MODEL_ID, "checkpoint_url": MODEL_URL, "checkpoint_sha256": MODEL_SHA256,
        "license": "MIT", "license_url": LICENSE_URL, "license_notice": "audio/LICENSE_CIS",
        "speaker": SPEAKER, "sample_rate_hz": RATE, "format": "mono WAV PCM signed 16-bit",
        "generation": "CPU, 2 threads, fixed seed 0, SSML prosody rate 94%; sentence-level segmentation; no time-stretch or pitch-shift",
        "source": "Prepared Lesson 115 scripts in narration/; content/videos.json contains the narrowly revised copy for the schematic-only Remotion production.",
        "videos": output, "elapsed_seconds": round(time.monotonic() - started, 3),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "human_review": "Generated audio is not author-listening-approved. Check pronunciation, emphasis, pace, and naturalness before any database import.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "speech_cues": len(rows), "seconds": round(sum(row["duration_seconds"] for entries in generated.values() for row in entries), 2), "provenance": str(report_path.relative_to(ROOT))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
