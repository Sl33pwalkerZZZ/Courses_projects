import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, openSync, closeSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { resolve, relative, join } from "node:path";

const root = process.cwd();
const mode = process.argv.includes("--preview") ? "preview" : process.argv.includes("--final") ? "final" : null;
if (!mode) throw new Error("Specify --preview or --final.");
let videos = JSON.parse(readFileSync("content/videos.json", "utf8"));
const selected = process.argv.find((arg) => arg.startsWith("--video="))?.split("=")[1];
if (selected) videos = videos.filter((video) => video.id === selected);
if (!videos.length) throw new Error("Unknown video selection.");

const hashFile = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");
function filesBelow(path) {
  if (!existsSync(path)) return [];
  return readdirSync(path, { withFileTypes: true }).flatMap((entry) => {
    const child = join(path, entry.name);
    return entry.isDirectory() ? filesBelow(child) : [child];
  });
}
const sourcePaths = ["src", "content", "scripts", "public", "audio/narration_sentences", "out/audio-sentence"]
  .flatMap(filesBelow).sort();
const inputs = Object.fromEntries(sourcePaths.map((path) => [relative(root, path), hashFile(path)]));
const freeze = JSON.stringify(inputs);
const qa = "out/qa";
mkdirSync(qa, { recursive: true });
mkdirSync("out/previews-v3", { recursive: true });
mkdirSync("out/final-sentence", { recursive: true });
if (mode === "final") {
  const reviewPath = `${qa}/frame-review.json`;
  if (!existsSync(reviewPath)) throw new Error("Inspect preview frames and create out/qa/frame-review.json first.");
  const review = JSON.parse(readFileSync(reviewPath, "utf8"));
  if (review.approved !== true || JSON.stringify(review.inputs) !== freeze)
    throw new Error("Preview-frame review does not match the current source hashes.");
}

async function run(command, args, logPath) {
  const fd = openSync(logPath, "w");
  try {
    await new Promise((resolvePromise, reject) => {
      const child = spawn(command, args, { cwd: root, stdio: ["ignore", fd, fd] });
      child.on("error", reject);
      child.on("exit", (code, signal) => code === 0 ? resolvePromise() : reject(new Error(`${command} exited ${code ?? signal}; see ${logPath}`)));
    });
  } finally {
    closeSync(fd);
  }
}

for (const video of videos) {
  const timing = JSON.parse(readFileSync("content/timings-sentence.json", "utf8"))[video.id];
  const prefix = mode === "preview" ? `out/previews-v3/${video.filename}-preview` : `out/final-sentence/${video.filename}`;
  const visual = `${prefix}-visual.mp4`;
  const target = mode === "preview" ? `${prefix}.mp4` : `${prefix}.mp4`;
  const mix = `out/audio-sentence/${video.filename}-mix.wav`;
  if (!existsSync(mix)) throw new Error(`Missing prepared audio mix: ${mix}`);
  if (existsSync(visual) || existsSync(target)) throw new Error(`Refusing to overwrite: ${visual} or ${target}`);
  const renderArgs = [
    "render", "src/index.tsx", video.composition, visual,
    "--codec=h264", `--crf=${mode === "preview" ? 21 : 18}`, `--concurrency=${process.env.REMOTION_CONCURRENCY || 2}`,
    "--pixel-format=yuv420p",
    ...(mode === "preview" ? ["--scale=0.5"] : []),
  ];
  console.log(`Rendering ${mode} ${video.id}: ${timing.durationSeconds}s`);
  await run(resolve("node_modules/.bin/remotion"), renderArgs, `${qa}/${video.id}-${mode}-layout-v3-visual.log`);
  const currentPaths = ["src", "content", "scripts", "public", "audio/narration_sentences", "out/audio-sentence"].flatMap(filesBelow).sort();
  const current = Object.fromEntries(currentPaths.map((path) => [relative(root, path), hashFile(path)]));
  if (JSON.stringify(current) !== freeze) throw new Error("Source changed during render; preserve output and investigate before continuing.");
  await run("ffmpeg", [
    "-v", "error", "-nostdin", "-n", "-i", visual, "-i", mix,
    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
    "-b:a", "320k", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", target,
  ], `${qa}/${video.id}-${mode}-layout-v3-mux.log`);
  if (mode === "preview") writeFileSync(`${qa}/${video.id}-preview-layout-v3-inputs.json`, JSON.stringify(inputs, null, 2) + "\n");
  console.log(`Created ${target}`);
}
