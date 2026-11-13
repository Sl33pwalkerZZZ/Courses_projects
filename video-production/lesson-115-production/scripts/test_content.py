"""Focused source, script and subtitle consistency checks; no database access."""
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_narration import normalized, model_stress

videos = json.loads((ROOT / "content/videos.json").read_text(encoding="utf-8"))
expected = [
    ("m5-l15-v1-export-check", "storyboards/m5-l15-v1-export-check.storyboard.md", "Экспорт проверочной версии в CapCut Desktop"),
    ("m5-l15-v2-vertical-adaptation", "storyboards/m5-l15-v2-vertical-adaptation.storyboard.md", "Адаптация 16:9 в 9:16"),
    ("m5-l15-v3-final-review", "storyboards/m5-l15-v3-final-review.storyboard.md", "Редакторская проверка перед публикацией"),
]
assert len(videos) == 3
for video, expected_row in zip(videos, expected):
    assert (video["id"], video["sourceStoryboard"], video["anchor"]) == expected_row
    assert len(video["scenes"]) == 6
    assert (ROOT / video["sourceStoryboard"]).is_file()
    assert video["lesson"] == 115
    assert video["plannedPlacement"].startswith("after section ")
    for scene in video["scenes"]:
        assert scene["title"] and scene["narration"] and scene["caption"] and scene["kind"]
        assert normalized(scene["narration"]) == normalized(scene["synthesis"])
        assert model_stress(scene["synthesis"])
        assert "CapCut" not in scene["narration"] or "версии" in scene["narration"]
        assert not any(claim in scene["caption"].lower() for claim in ("экспорт завершён", "разрешение подтверждено", "проверка пройдена"))

assert "СХЕМА ИНТЕРФЕЙСА · НЕ ЗАПИСЬ CAPCUT" in (ROOT / "src/tokens.ts").read_text(encoding="utf-8")
assert "out/final" not in (ROOT / "content/videos.json").read_text(encoding="utf-8")
assert "course 10" not in (ROOT / "scripts/generate_narration.py").read_text(encoding="utf-8").lower()
print("PASS: three existing targets, six storyboard scenes each, narration text/stress identity and illustration disclosure.")
