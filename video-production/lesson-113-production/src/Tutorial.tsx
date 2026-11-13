import type { CalculateMetadataFunction } from "remotion";
import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  interpolate,
  Sequence,
  staticFile,
  Track,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import data from "../content/videos.json";
import cues from "../content/sfx-cues.json";
import { design as d } from "./tokens";
import {
  AnimatedTitle,
  Background,
  clamp,
  FrameChrome,
  InstructionCaption,
  PanelShell,
  StepIndicator,
} from "./primitives";
import { Visual } from "./visuals";
import type { TutorialData, Scene, Cue } from "./types";
import "./fonts";

export type TutorialProps = {
  videoId: string;
  sfxVolume: number;
  muteSfx: boolean;
};
const LessonScene = ({
  scene,
  index,
  total,
}: {
  scene: Scene;
  index: number;
  total: number;
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        opacity: interpolate(
          f,
          [(scene.seconds - 0.3) * fps, scene.seconds * fps],
          [1, 0],
          clamp,
        ),
      }}
    >
      <AnimatedTitle>{scene.title}</AnimatedTitle>
      <InstructionCaption instruction={scene.instruction} note={scene.note} />
      <PanelShell label="ИЛЛЮСТРАЦИЯ / Ф1">
        <Visual kind={scene.visual} at={scene.actionAt} />
      </PanelShell>
      <StepIndicator current={index} total={total} />
    </AbsoluteFill>
  );
};
export const SfxSynchronization = ({
  videoId,
  volume,
  muted,
}: {
  videoId: string;
  volume: number;
  muted: boolean;
}) => {
  const track = (cues as Record<string, Cue[]>)[videoId];
  return (
    <Track name="Original procedural SFX">
      {track.map((cue, index) => (
        <Audio
          key={`${cue.scene}-${index}`}
          name={`${cue.scene} / ${cue.sound}`}
          from={cue.frame}
          durationInFrames={cue.duration}
          src={staticFile(`sfx/${cue.sound}.wav`)}
          volume={Math.max(0, Math.min(1, volume)) * cue.gain}
          muted={muted}
        />
      ))}
    </Track>
  );
};
export const Tutorial = ({
  videoId,
  sfxVolume = 0.4,
  muteSfx = false,
}: TutorialProps) => {
  const video = (data as TutorialData[]).find((v) => v.id === videoId);
  const { fps } = useVideoConfig();
  if (!video) throw new Error("Unknown tutorial data");
  let start = 0;
  return (
    <AbsoluteFill
      className="lesson113-video"
      style={{ fontFamily: d.font, color: d.ink, overflow: "hidden" }}
    >
      <style>{`.lesson113-video, .lesson113-video * {box-sizing:border-box}`}</style>
      <Background />
      <Track name="Text-led instructional scenes">
        {video.scenes.map((scene, index) => {
          const from = start;
          start += scene.seconds;
          return (
            <Sequence
              key={scene.id}
              name={scene.title}
              from={from * fps}
              durationInFrames={scene.seconds * fps}
            >
              <LessonScene
                scene={scene}
                index={index}
                total={video.scenes.length}
              />
            </Sequence>
          );
        })}
      </Track>
      <SfxSynchronization
        videoId={video.id}
        volume={sfxVolume}
        muted={muteSfx}
      />
      <FrameChrome number={video.number} title={video.title} />
      {/* Future approved narration/captions get independent tracks here. No spoken track or fabricated subtitles in this package. */}
    </AbsoluteFill>
  );
};

export const calculateTutorialMetadata: CalculateMetadataFunction<
  TutorialProps
> = ({ props }) => {
  const video = (data as TutorialData[]).find((v) => v.id === props.videoId);
  if (!video) throw new Error("Unknown tutorial duration");
  return {
    durationInFrames:
      video.scenes.reduce((seconds, scene) => seconds + scene.seconds, 0) * 30,
  };
};
