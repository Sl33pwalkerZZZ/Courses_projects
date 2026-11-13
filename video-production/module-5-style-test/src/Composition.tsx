import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  Track,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { design as d, timing } from "./tokens";
import "./fonts";

const ease = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  easing: Easing.bezier(0.2, 0.8, 0.2, 1),
} as const;
const linear = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: d.background, overflow: "hidden" }}>
      <svg
        width="1920"
        height="1080"
        style={{
          position: "absolute",
          opacity: 0.4,
          translate: interpolate(
            frame,
            [0, 12 * fps],
            ["0px 0px", "-16px 0px"],
            linear,
          ),
        }}
        aria-hidden="true"
      >
        <defs>
          <pattern
            id="grid"
            width="96"
            height="96"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 96 0 L 0 0 0 96"
              fill="none"
              stroke="#2d3038"
              strokeWidth="1"
            />
          </pattern>
        </defs>
        <rect x="1030" y="0" width="1100" height="1080" fill="url(#grid)" />
        <path
          d="M940 1080 L1770 0 M1230 1080 L1920 200"
          stroke="#3a3d46"
          strokeWidth="1"
        />
        <circle cx="1650" cy="900" r="580" fill="none" stroke="#343741" />
      </svg>
    </AbsoluteFill>
  );
};

const FrameChrome: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{ pointerEvents: "none", fontSize: 22, color: d.muted }}
    >
      <div
        style={{
          position: "absolute",
          left: 128,
          top: 64,
          display: "flex",
          alignItems: "center",
          gap: 18,
        }}
      >
        <svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">
          <path
            d="M2 23 15 2 28 23ZM8 23 15 11 22 23"
            fill="none"
            stroke={d.lavender}
            strokeWidth="2"
          />
        </svg>
        <span style={{ fontWeight: 700, color: d.ink, letterSpacing: 2 }}>
          AI COURSES
        </span>
        <span style={{ marginLeft: 18 }}>МОДУЛЬ 05</span>
      </div>
      <div
        style={{ position: "absolute", right: 128, top: 67, letterSpacing: 2 }}
      >
        ВИЗУАЛЬНЫЙ ТЕСТ / 12 СЕК
      </div>
      <div style={{ position: "absolute", left: 128, bottom: 70 }}>
        Иллюстрация интерфейса · не запись CapCut
      </div>
      <div
        style={{ position: "absolute", right: 128, bottom: 70, color: d.ink }}
      >
        ИДЕЯ → СТРУКТУРА → МОНТАЖ
      </div>
      <div
        style={{
          position: "absolute",
          left: 128,
          right: 128,
          bottom: 48,
          height: 2,
          background: d.line,
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${interpolate(frame, [0, durationInFrames - 1], [0, 100])}%`,
            background: d.lavender,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

const RevealLine: React.FC<{
  children: React.ReactNode;
  delay?: number;
  color?: string;
  size?: number;
}> = ({ children, delay = 0, color = d.ink, size = 114 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ overflow: "hidden", paddingBottom: 14 }}>
      <div
        data-text-check="true"
        style={{
          fontSize: size,
          fontWeight: 700,
          letterSpacing: -5,
          lineHeight: 1.08,
          color,
          translate: interpolate(
            frame,
            [delay * fps, (delay + timing.entrance) * fps],
            ["0px 140px", "0px 0px"],
            ease,
          ),
          opacity: interpolate(
            frame,
            [delay * fps, (delay + 0.4) * fps],
            [0, 1],
            linear,
          ),
        }}
      >
        {children}
      </div>
    </div>
  );
};

const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        opacity: interpolate(frame, [2.95 * fps, 3.4 * fps], [1, 0], linear),
      }}
    >
      <div style={{ position: "absolute", left: 128, top: 250, width: 1010 }}>
        <p
          style={{
            fontSize: 25,
            letterSpacing: 3,
            color: d.lavender,
            marginBottom: 36,
          }}
        >
          01 / НАЧИНАЕМ СО СТРУКТУРЫ
        </p>
        <h1 style={{ margin: 0 }}>
          <RevealLine size={120}>От идеи</RevealLine>
          <RevealLine delay={0.16} size={120} color={d.lavender}>
            к видеопроекту
          </RevealLine>
        </h1>
        <p
          data-text-check="true"
          style={{
            fontSize: 32,
            color: d.muted,
            marginTop: 36,
            opacity: interpolate(frame, [0.7 * fps, 1.2 * fps], [0, 1], linear),
            translate: interpolate(
              frame,
              [0.7 * fps, 1.4 * fps],
              ["0px 18px", "0px 0px"],
              ease,
            ),
          }}
        >
          Сначала порядок. Затем творчество.
        </p>
      </div>
    </AbsoluteFill>
  );
};

const Organize: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        opacity: interpolate(frame, [3.95 * fps, 4.4 * fps], [1, 0], linear),
      }}
    >
      <div style={{ position: "absolute", left: 128, top: 164 }}>
        <p
          style={{
            fontSize: 25,
            letterSpacing: 3,
            color: d.mint,
            margin: "0 0 24px",
          }}
        >
          02 / У КАЖДОГО ФАЙЛА СВОЁ МЕСТО
        </p>
        <RevealLine size={96}>Организуем материалы</RevealLine>
      </div>
      <div
        data-text-check="true"
        style={{
          position: "absolute",
          left: 128,
          top: 845,
          fontSize: 29,
          color: d.muted,
          opacity: interpolate(frame, [0.9 * fps, 1.4 * fps], [0, 1], linear),
        }}
      >
        Видео, звук, изображения и готовые версии — отдельно.
      </div>
    </AbsoluteFill>
  );
};

const Ready: React.FC = () => {
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 128, top: 164 }}>
        <p
          style={{
            fontSize: 25,
            letterSpacing: 3,
            color: d.lavender,
            margin: "0 0 24px",
          }}
        >
          03 / ОТ ПАПОК К ИСТОРИИ
        </p>
        <RevealLine size={106}>Готово к монтажу</RevealLine>
        <div
          data-text-check="true"
          style={{ fontSize: 30, color: d.muted, marginTop: 18 }}
        >
          Материалы на своих местах. Можно собирать историю.
        </div>
      </div>
    </AbsoluteFill>
  );
};

const DocumentRows: React.FC<{ file: string; accent: string }> = ({
  file,
  accent,
}) => (
  <div style={{ padding: "0 28px" }}>
    <div
      style={{
        display: "flex",
        gap: 14,
        alignItems: "center",
        fontSize: 23,
        color: d.ink,
        marginBottom: 24,
      }}
    >
      <svg width="24" height="28" viewBox="0 0 24 28" aria-hidden="true">
        <path
          d="M3 1H15L22 8V26H3Z M15 1V8H22"
          fill="none"
          stroke={accent}
          strokeWidth="1.5"
        />
      </svg>
      {file}
    </div>
    <div
      style={{ height: 4, width: "78%", background: d.line, marginBottom: 15 }}
    />
    <div style={{ height: 4, width: "53%", background: d.line }} />
  </div>
);

const FolderToTrack: React.FC<{
  index: number;
  title: string;
  file: string;
  accent: string;
}> = ({ index, title, file, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = (timing.organizeStart + index * 0.13) * fps;
  const b = (timing.organizeEnd + index * 0.07) * fps;
  const c = (timing.transformStart + index * 0.04) * fps;
  const e = (timing.transformEnd + index * 0.04) * fps;
  const morph = interpolate(frame, [c, e], [0, 1], ease);
  const width = interpolate(frame, [c, e], [388, 1664], ease);
  const height = interpolate(frame, [c, e], [300, 72], ease);
  return (
    <div
      data-visual="folder-track"
      style={{
        position: "absolute",
        left: interpolate(
          frame,
          [a, b, c, e],
          [1215 + index * 24, 128 + index * 425, 128 + index * 425, 128],
          ease,
        ),
        top: interpolate(
          frame,
          [a, b, c, e],
          [395 - index * 30, 468, 468, 466 + index * 90],
          ease,
        ),
        width,
        height,
        rotate: interpolate(
          frame,
          [a, b, c, e],
          [`${-9 + index * 7}deg`, "0deg", "0deg", "0deg"],
          ease,
        ),
        opacity: interpolate(
          frame,
          [
            (index === 0 ? 0.25 : timing.organizeStart + index * 0.15) * fps,
            (index === 0 ? 1.1 : timing.organizeStart + index * 0.15 + 0.5) *
              fps,
          ],
          [0, 1],
          linear,
        ),
        scale: interpolate(frame, [0.25 * fps, 1.3 * fps], [1.1, 1], {
          ...ease,
          output: "perceptual-scale",
        }),
        zIndex: 5 - index,
      }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 388 300"
        preserveAspectRatio="none"
        style={{
          position: "absolute",
          overflow: "visible",
          opacity: 1 - morph,
        }}
        aria-hidden="true"
      >
        <path
          d="M0 36Q0 20 16 20H119L143 0H226Q242 0 242 20V36H372Q388 36 388 52V284Q388 300 372 300H16Q0 300 0 284Z"
          fill={d.surface}
          stroke={accent}
          strokeWidth="1.2"
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          border: `1px solid ${d.line}`,
          borderRadius: 8,
          background: d.surface,
          opacity: morph,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 28,
          top: interpolate(frame, [c, e], [61, 22], ease),
          fontSize: interpolate(frame, [c, e], [29, 23], ease),
          fontWeight: 700,
          color: accent,
          letterSpacing: 1,
        }}
      >
        <span
          style={{
            opacity: interpolate(frame, [a, b], [index === 0 ? 0 : 1, 1], ease),
          }}
        >
          {title}
        </span>
      </div>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 132,
          opacity:
            interpolate(frame, [c, c + 0.32 * fps], [1, 0], linear) *
            interpolate(frame, [a, b], [0, 1], ease),
        }}
      >
        <DocumentRows file={file} accent={accent} />
      </div>
      {index === 0 && (
        <div
          style={{
            position: "absolute",
            left: 35,
            top: 74,
            opacity: interpolate(frame, [a, b], [1, 0], ease),
          }}
        >
          <div
            style={{
              fontSize: 112,
              fontWeight: 700,
              color: d.lavender,
              letterSpacing: -5,
            }}
          >
            F1
            <span style={{ color: d.muted, fontSize: 28, marginLeft: 18 }}>
              ПРОЕКТ
            </span>
          </div>
          <div style={{ fontSize: 22, color: d.muted }}>
            Вымышленный учебный пример
          </div>
        </div>
      )}
      <div
        style={{
          position: "absolute",
          left: 286,
          right: 18,
          top: 13,
          bottom: 13,
          display: "flex",
          gap: 12,
          opacity: morph,
        }}
      >
        <div
          style={{
            flex: index === 2 ? 1.3 : 2,
            background: accent,
            borderRadius: 4,
            position: "relative",
            overflow: "hidden",
          }}
        >
          {index === 1 ? (
            <svg
              width="100%"
              height="100%"
              viewBox="0 0 600 46"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <path
                d={Array.from(
                  { length: 150 },
                  (_, i) =>
                    `M${i * 4} ${23 - (5 + Math.sin(i * 0.71) ** 2 * 13)}v${10 + Math.sin(i * 0.71) ** 2 * 26}`,
                ).join(" ")}
                stroke={d.background}
                strokeWidth="2"
              />
            </svg>
          ) : (
            <span
              style={{
                fontSize: 23,
                color: d.background,
                position: "absolute",
                left: 18,
                top: 5,
                fontWeight: 700,
              }}
            >
              {index === 0
                ? "СЦЕНА 01"
                : index === 2
                  ? "ГРАФИКА"
                  : "ГОТОВАЯ ВЕРСИЯ"}
            </span>
          )}
        </div>
        <div
          style={{
            flex: index === 0 ? 1.5 : 1,
            background: accent,
            borderRadius: 4,
            opacity: 0.45,
          }}
        />
        <div
          style={{
            flex: 0.65,
            background: accent,
            borderRadius: 4,
            opacity: 0.24,
          }}
        />
      </div>
    </div>
  );
};

const TimelineRuler: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: 414,
        top: 417,
        width: 1360,
        height: 392,
        zIndex: 8,
        opacity: interpolate(frame, [8.65 * fps, 9.3 * fps], [0, 1], ease),
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 22,
          color: d.muted,
        }}
      >
        <span>00:00</span>
        <span>00:04</span>
        <span>00:08</span>
        <span>00:12</span>
      </div>
      <div
        style={{
          position: "absolute",
          top: 40,
          bottom: 0,
          width: 2,
          background: d.ink,
          left: interpolate(frame, [9.2 * fps, 11.7 * fps], [20, 1200], ease),
        }}
      >
        <div
          style={{
            width: 12,
            height: 12,
            rotate: "45deg",
            background: d.ink,
            marginLeft: -5,
          }}
        />
      </div>
    </div>
  );
};

// One composition, three editable text-scene boundaries. The continuous illustration
// sits on its own layer, so folders genuinely travel into the final timeline.
export const ProjectFilesPrototype: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{ fontFamily: d.font, color: d.ink, overflow: "hidden" }}
    >
      <Backdrop />
      <Track name="Three connected scenes">
        <Sequence
          name="01 — От идеи к видеопроекту"
          durationInFrames={3.4 * fps}
        >
          <Opening />
        </Sequence>
        <Sequence
          name="02 — Организуем материалы"
          from={3.4 * fps}
          durationInFrames={4.4 * fps}
        >
          <Organize />
        </Sequence>
        <Sequence
          name="03 — Готово к монтажу"
          from={7.8 * fps}
          durationInFrames={4.2 * fps}
        >
          <Ready />
        </Sequence>
      </Track>
      <Sequence
        name="Continuous folder-to-timeline illustration"
        durationInFrames={12 * fps}
      >
        <FolderToTrack
          index={0}
          title="01_VIDEO"
          file="сцена_01.mp4"
          accent={d.lavender}
        />
        <FolderToTrack
          index={1}
          title="02_AUDIO"
          file="озвучка.wav"
          accent={d.mint}
        />
        <FolderToTrack
          index={2}
          title="03_IMAGES"
          file="обложка.png"
          accent={d.blue}
        />
        <FolderToTrack
          index={3}
          title="04_EXPORT"
          file="готовое_видео.mp4"
          accent={d.sand}
        />
        <TimelineRuler />
      </Sequence>
      {/* Future narration/caption tracks belong here, independently of scene timing.
        This style test intentionally has no Audio, media inputs or burned-in captions. */}
      <FrameChrome />
    </AbsoluteFill>
  );
};
