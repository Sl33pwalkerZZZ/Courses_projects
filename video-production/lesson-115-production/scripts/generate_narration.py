"""Generate non-overwriting Russian Lesson 115 narration with the retained Silero CIS Base model."""
from array import array
import argparse
import hashlib
import importlib
import json
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


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def normalized(raw: str) -> str:
    decomposed = unicodedata.normalize("NFD", raw.replace("+", "").replace("`", ""))
    plain = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return " ".join(unicodedata.normalize("NFC", plain).split())


def model_stress(raw: str) -> str:
    """Convert readable acute stress marks to the checkpoint's prefix-plus syntax."""
    decomposed = unicodedata.normalize("NFD", raw)
    output: list[str] = []
    for char in decomposed:
        if char == "\u0301":
            if not output or output[-1] not in "аеёиоуыэюяАЕЁИОУЫЭЮЯ":
                raise ValueError("Stress mark is not attached to a Russian vowel.")
            vowel = output.pop()
            output.extend(("+", vowel))
        else:
            output.append(char)
    return unicodedata.normalize("NFC", "".join(output))


def write_wav(path: Path, samples: array) -> None:
    if sys.byteorder != "little":
        samples.byteswap()
    with wave.open(str(path), "wb") as out:
        out.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        out.writeframes(samples.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    if not args.checkpoint.is_file() or sha(args.checkpoint.read_bytes()) != MODEL_SHA256:
        raise SystemExit("Checkpoint is absent or its verified SHA-256 does not match.")
    source = json.loads((ROOT / "content/videos.json").read_text(encoding="utf-8"))
    output_root = ROOT / "audio/narration"
    targets = [output_root / video["id"] / f"scene-{index + 1:02}.wav" for video in source for index, _ in enumerate(video["scenes"])]
    report_path = ROOT / "content/narration-provenance.json"
    if report_path.exists() or any(path.exists() for path in targets):
        raise SystemExit("Refusing to overwrite existing narration outputs or provenance.")
    output_root.mkdir(parents=True, exist_ok=True)

    import torch
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    model = torch.package.PackageImporter(str(args.checkpoint)).load_pickle("tts_models", "model")
    model.to(torch.device("cpu"))
    if SPEAKER not in model.speakers:
        raise SystemExit("Required Russian speaker ru_roman is not present in this checkpoint.")

    generated: list[dict] = []
    started = time.monotonic()
    try:
        for video in source:
            for index, scene in enumerate(video["scenes"], 1):
                if normalized(scene["synthesis"]) != normalized(scene["narration"]):
                    raise SystemExit(f"Stress-marked text changes spoken copy: {video['id']} scene {index}")
                marked = model_stress(scene["synthesis"])
                ssml = f'<speak><prosody rate="94%">{escape(marked)}</prosody></speak>'
                with torch.inference_mode():
                    tensor = model.apply_tts(ssml_text=ssml, speaker=SPEAKER, sample_rate=RATE).detach().cpu().flatten()
                if not bool(torch.isfinite(tensor).all()) or tensor.numel() < RATE // 4:
                    raise SystemExit(f"Invalid or very short synthesis: {video['id']} scene {index}")
                peak = float(tensor.abs().max())
                if not 0 < peak < 1:
                    raise SystemExit(f"Silent or clipped synthesis: {video['id']} scene {index}")
                pcm = array("h", (round(float(value) * 32767) for value in tensor.tolist()))
                target = output_root / video["id"] / f"scene-{index:02}.wav"
                target.parent.mkdir(parents=True, exist_ok=True)
                write_wav(target, pcm)
                raw = target.read_bytes()
                generated.append({
                    "video": video["id"], "scene": index, "path": str(target.relative_to(ROOT)),
                    "text": scene["narration"], "synthesis_input": scene["synthesis"], "ssml": ssml,
                    "samples": len(pcm), "duration_seconds": len(pcm) / RATE, "sha256": sha(raw),
                    "peak_dbfs": round(20 * __import__("math").log10(peak), 3),
                })
    except Exception:
        # Keep any already-created files for diagnosis; never delete local production work automatically.
        raise

    report = {
        "status": "generated_candidates_pending_human_voice_review",
        "model_id": MODEL_ID, "checkpoint_url": MODEL_URL, "checkpoint_sha256": MODEL_SHA256,
        "license": "MIT", "license_url": LICENSE_URL, "license_notice": "Retained in audio/LICENSE_CIS",
        "speaker": SPEAKER, "sample_rate_hz": RATE, "format": "mono WAV PCM signed 16-bit",
        "generation": "CPU, 2 threads, fixed seed 0, native SSML prosody rate 94%; no time-stretch or pitch-shift",
        "source": "content/videos.json; narration wording follows the Lesson 115 prepared scripts with targeted changes to avoid claiming real CapCut operations or measured export results.",
        "outputs": generated, "elapsed_seconds": round(time.monotonic() - started, 3),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "review_required": ["Listen to every Russian phrase, proper name, numeric expression, stress and paragraph join.", "Confirm the voice performance before any protected-media import.", "MIT model license does not itself constitute author approval of a particular narration or course attachment."],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "segments": len(generated), "seconds": round(sum(item["duration_seconds"] for item in generated), 2), "report": str(report_path.relative_to(ROOT))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
