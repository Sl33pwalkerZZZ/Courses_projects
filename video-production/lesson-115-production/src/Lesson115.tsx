import {
  AbsoluteFill,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Background, ease } from "../../lesson-113-production/src/primitives";
import { design as d, illustrationDisclosure } from "./tokens";
import { SceneVisual } from "./SceneVisual";
import videos from "../content/videos.json";
import timings from "../content/timings-sentence.json";
import "./fonts";

type VideoId = (typeof videos)[number]["id"];
type Props = { videoId: VideoId };

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const getVideo = (id: VideoId) => videos.find((video) => video.id === id)!;
const getTiming = (id: VideoId) => timings[id as keyof typeof timings];

const Scene: React.FC<{
  title: string;
  kind: string;
  caption: string;
  captions: { startFrame: number; durationFrames: number; text: string }[];
  index: number;
  total: number;
}> = ({ title, kind, caption, captions, index, total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleY = interpolate(frame, [0, fps * 0.65], [54, 0], ease);
  const currentCaption = captions.find((cue) => frame >= cue.startFrame && frame < cue.startFrame + cue.durationFrames);
  const captionOpacity = currentCaption ? interpolate(frame, [currentCaption.startFrame, currentCaption.startFrame + 8], [0, 1], clamp) : 0;
  return (
    <AbsoluteFill style={{ fontFamily: d.font, color: d.ink }}>
      <Background />
      <header style={{ position: "absolute", top: 54, left: 128, right: 128, display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 20, color: d.muted }}>
        <span><b style={{ color: d.ink, letterSpacing: 1.2, marginRight: 20 }}>AI COURSES</b>УРОК 115</span>
        <span>{String(index + 1).padStart(2, "0")} / {String(total).padStart(2, "0")}</span>
      </header>
      <div style={{ position: "absolute", left: 128, top: 144, width: 1500, overflow: "hidden", paddingBottom: 12 }}>
        <h1 data-read="true" style={{ margin: 0, fontSize: 66, lineHeight: 1.12, letterSpacing: -2.4, fontWeight: 700, color: d.ink, transform: `translateY(${titleY}px)` }}>{title}</h1>
      </div>
      <div style={{ position: "absolute", right: 128, top: 244, fontSize: 17, letterSpacing: 1.3, color: d.sand }}>{illustrationDisclosure}</div>
      <div style={{ position: "absolute", left: 128, top: 303, width: 540, height: 466, borderTop: `1px solid ${d.line}`, paddingTop: 26 }}>
        <div style={{ color: d.muted, fontSize: 17, letterSpacing: 1, marginBottom: 24 }}>УЧЕБНЫЙ ПРИМЕР · Ф1</div>
        <div data-read="true" style={{ color: d.ink, fontSize: 34, lineHeight: 1.34, fontWeight: 600 }}>{caption}</div>
        <div style={{ position: "absolute", left: 0, bottom: 16, width: 98, height: 3, background: d.lavender, transform: `scaleX(${interpolate(frame, [0, fps * 0.8], [0, 1], clamp)})`, transformOrigin: "left" }} />
      </div>
      <section data-panel="illustration" style={{ position: "absolute", left: 708, top: 306, width: 1084, height: 492, border: `1px solid ${d.line}`, borderRadius: 14, background: d.surface, overflow: "hidden" }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 54, borderBottom: `1px solid ${d.line}`, display: "flex", alignItems: "center", padding: "0 24px", color: d.muted, fontSize: 17, letterSpacing: 0.6 }}>
          <span>ПОЯСНИТЕЛЬНАЯ ИЛЛЮСТРАЦИЯ</span><span style={{ marginLeft: "auto", color: d.sand }}>НЕ ФАКТИЧЕСКИЙ ВЫВОД ПРОГРАММЫ</span>
        </div>
        <SceneVisual kind={kind} />
      </section>
      <footer style={{ position: "absolute", left: 128, right: 128, bottom: 50, display: "flex", justifyContent: "space-between", color: d.muted, fontSize: 17 }}>
        <span>СХЕМА · ПРОВЕРЯЙТЕ ДЕЙСТВИЯ В СВОЕЙ ВЕРСИИ РЕДАКТОРА</span>
        <span>{index + 1} / {total}</span>
      </footer>
      {currentCaption && <div data-caption="spoken" style={{ position: "absolute", left: 128, right: 128, bottom: 88, minHeight: 74, padding: "18px 26px", border: `1px solid ${d.line}`, borderRadius: 10, background: d.background, color: d.ink, fontSize: 28, lineHeight: 1.34, opacity: captionOpacity }}>{currentCaption.text.replace(/`/g, "")}</div>}
    </AbsoluteFill>
  );
};

export const Lesson115: React.FC<Props> = ({ videoId }) => {
  const video = getVideo(videoId);
  const layout = getTiming(videoId);
  return (
    <AbsoluteFill style={{ background: d.background, fontFamily: d.font }}>
      {video.scenes.map((scene, index) => {
        const time = layout.scenes[index];
        return (
          <Sequence key={scene.kind} from={time.startFrame} durationInFrames={time.durationFrames}>
            <Scene title={scene.title} kind={scene.kind} caption={scene.caption} captions={time.captions} index={index} total={video.scenes.length} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const calculateMetadata = ({ props }: { props: Props }) => ({
  durationInFrames: getTiming(props.videoId).durationFrames,
});
