"""Extract one readable representative frame per scene from preview exports."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
videos = json.loads((ROOT / "content/videos.json").read_text(encoding="utf-8"))
timings = json.loads((ROOT / "content/timings-sentence.json").read_text(encoding="utf-8"))
out = ROOT / "out/qa/frames-v2"
out.mkdir(parents=True, exist_ok=True)
for video in videos:
    preview = ROOT / "out/previews-v3" / f"{video['filename']}-preview.mp4"
    if not preview.is_file():
        raise SystemExit(f"Missing preview: {preview}")
    for index, scene in enumerate(timings[video["id"]]["scenes"], 1):
        seconds = scene["startFrame"] / 30 + min(3.0, scene["durationFrames"] / 30 / 2)
        target = out / f"{video['id']}-scene-{index:02}.png"
        if target.exists():
            raise SystemExit(f"Refusing to overwrite frame: {target}")
        subprocess.run([
            "ffmpeg", "-v", "error", "-nostdin", "-ss", f"{seconds:.3f}", "-i", str(preview),
            "-frames:v", "1", "-vf", "scale=960:540", str(target),
        ], check=True)
print(f"Extracted {sum(len(video['scenes']) for video in videos)} preview frames to {out.relative_to(ROOT)}")
