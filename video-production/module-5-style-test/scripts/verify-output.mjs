import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";

const results = [];
for (const [file, width, height] of [
  ["out/module-5-style-preview-960x540.mp4", 960, 540],
  ["out/module-5-style-1920x1080.mp4", 1920, 1080],
]) {
  const metadata = JSON.parse(
    execFileSync(
      "ffprobe",
      ["-v", "error", "-show_streams", "-show_format", "-of", "json", file],
      { encoding: "utf8" },
    ),
  );
  assert.equal(metadata.streams.length, 1, "The style test must remain silent");
  const video = metadata.streams[0];
  assert.equal(video.codec_name, "h264");
  assert.equal(video.width, width);
  assert.equal(video.height, height);
  assert.equal(video.r_frame_rate, "30/1");
  assert.equal(Number(video.nb_frames), 360);
  assert.equal(Number(metadata.format.duration), 12);
  assert.equal(video.pix_fmt, "yuv420p");
  execFileSync(
    "ffmpeg",
    ["-v", "error", "-xerror", "-nostdin", "-i", file, "-f", "null", "-"],
    { stdio: "pipe" },
  );
  results.push({
    file,
    width,
    height,
    fps: 30,
    frames: 360,
    duration: 12,
    audio: false,
    bytes: readFileSync(file).length,
    sha256: createHash("sha256").update(readFileSync(file)).digest("hex"),
    decode: "PASS",
  });
}
writeFileSync("out/verification.json", JSON.stringify(results, null, 2) + "\n");
console.log(JSON.stringify(results, null, 2));
