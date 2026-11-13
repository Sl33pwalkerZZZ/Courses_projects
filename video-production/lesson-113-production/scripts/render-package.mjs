import { spawn, execFileSync } from "node:child_process";
import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  openSync,
  closeSync,
} from "node:fs";
import { resolve } from "node:path";

const preview = process.argv.includes("--preview");
if (!preview && !process.argv.includes("--final"))
  throw Error("Use --preview or --final");
let videos = JSON.parse(readFileSync("content/videos.json", "utf8"));
const selected = process.argv
  .find((arg) => arg.startsWith("--video="))
  ?.split("=")[1];
if (selected) videos = videos.filter((video) => video.id === selected);
if (!videos.length) throw new Error("Unknown video selection");
mkdirSync("out/previews", { recursive: true });
mkdirSync("out/final", { recursive: true });
mkdirSync("out/logs", { recursive: true });
if (!preview) {
  const review = JSON.parse(readFileSync("out/qa/frame-review.json", "utf8"));
  if (
    review.approved !== true ||
    review.scenes !== videos.reduce((n, v) => n + v.scenes.length, 0)
  )
    throw Error(
      "Inspect every preview scene and record frame review before final renders.",
    );
}
const statuses = [];
for (const v of videos) {
  const output = `out/${preview ? "previews" : "final"}/${v.filename}${preview ? "-preview" : ""}.mp4`;
  if (process.argv.includes("--resume")) {
    try {
      const m = JSON.parse(
        execFileSync(
          "ffprobe",
          [
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=nb_frames,width,height",
            "-of",
            "json",
            output,
          ],
          { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] },
        ),
      );
      if (
        Number(m.streams[0].nb_frames) === v.seconds * 30 &&
        m.streams[0].width === (preview ? 960 : 1920)
      ) {
        console.log("KEEP verified complete output:", output);
        continue;
      }
    } catch {
      /* Missing/incomplete task-generated output: render it. */
    }
  }
  const fd = openSync(
    `out/logs/${v.id}-${preview ? "preview" : "final"}.log`,
    "w",
  );
  const args = [
    "render",
    v.composition,
    output,
    "--codec=h264",
    "--audio-codec=aac",
    `--crf=${preview ? 21 : 18}`,
    `--concurrency=${Math.min(4, Math.max(1, Number(process.env.REMOTION_CONCURRENCY || 2)))}`,
    ...(preview ? ["--scale=0.5"] : []),
  ];
  console.log(
    "Rendering",
    v.composition,
    preview ? "960x540 preview" : "1920x1080 final",
    v.seconds,
    "seconds",
  );
  const result = await new Promise((success, failure) => {
    const child = spawn(resolve("node_modules/.bin/remotion"), args, {
      stdio: ["ignore", fd, fd],
    });
    child.on("error", failure);
    child.on("exit", (code, signal) => success({ code, signal }));
  });
  closeSync(fd);
  statuses.push({ video: v.id, output, ...result });
  writeFileSync(
    `out/${preview ? "preview" : "final"}-render-status.json`,
    JSON.stringify(statuses, null, 2),
  );
  if (result.code !== 0)
    throw Error(
      `Render failed for ${v.id}: ${JSON.stringify(result)}. Inspect output/logs; do not assume success.`,
    );
  console.log("Complete:", output);
}
