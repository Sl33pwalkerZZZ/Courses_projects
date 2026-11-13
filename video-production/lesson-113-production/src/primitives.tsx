import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { design as d } from "./tokens";

export const ease = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  easing: Easing.bezier(0.2, 0.8, 0.2, 1),
} as const;
export const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;
export const Label: React.FC<React.PropsWithChildren<{ color?: string }>> = ({
  children,
  color = d.muted,
}) => (
  <div data-read="true" style={{ fontSize: 26, color, lineHeight: 1.4 }}>
    {children}
  </div>
);
export const Paper: React.FC<{
  notepad?: boolean;
  width?: number;
  height?: number;
}> = ({ notepad = false, width = 220, height = 180 }) => (
  <Img
    src={staticFile(`f1/f1-${notepad ? "notepad" : "paper"}-diagram.svg`)}
    style={{ width, height, objectFit: "contain" }}
  />
);

export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: d.background }}>
      <svg
        width="1920"
        height="1080"
        style={{
          position: "absolute",
          opacity: 0.4,
          translate: interpolate(
            frame,
            [0, durationInFrames],
            ["0px 0px", "-16px 0px"],
            clamp,
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
            <path d="M96 0H0V96" fill="none" stroke="#2d3038" />
          </pattern>
        </defs>
        <rect x="1030" width="1100" height="1080" fill="url(#grid)" />
        <path
          d="M940 1080L1770 0M1230 1080L1920 200"
          stroke="#3a3d46"
          fill="none"
        />
        <circle cx="1650" cy="900" r="580" fill="none" stroke="#343741" />
      </svg>
    </AbsoluteFill>
  );
};
export const AnimatedTitle: React.FC<{ children: string }> = ({ children }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: 128,
        top: 172,
        width: 1664,
        overflow: "hidden",
        paddingBottom: 12,
      }}
    >
      <h1
        data-read="true"
        style={{
          margin: 0,
          fontWeight: 700,
          fontSize: 84,
          letterSpacing: -3.5,
          lineHeight: 1.14,
          color: d.ink,
          translate: interpolate(
            f,
            [0, 0.8 * fps],
            ["0px 120px", "0px 0px"],
            ease,
          ),
        }}
      >
        {children}
      </h1>
    </div>
  );
};
export const InstructionCaption: React.FC<{
  instruction: string;
  note: string;
}> = ({ instruction, note }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: 128,
        top: 350,
        width: 620,
        opacity: interpolate(f, [0.35 * fps, 0.9 * fps], [0, 1], clamp),
        translate: interpolate(
          f,
          [0.35 * fps, 0.9 * fps],
          ["0px 16px", "0px 0px"],
          ease,
        ),
      }}
    >
      <p
        data-read="true"
        style={{
          fontSize: 43,
          fontWeight: 700,
          lineHeight: 1.25,
          letterSpacing: -1,
          margin: 0,
          color: d.ink,
        }}
      >
        {instruction}
      </p>
      <div
        style={{
          width: 64,
          height: 2,
          background: d.lavender,
          margin: "36px 0 26px",
        }}
      />
      <p
        data-read="true"
        style={{ fontSize: 28, lineHeight: 1.5, margin: 0, color: d.muted }}
      >
        {note}
      </p>
    </div>
  );
};
export const PanelShell: React.FC<
  React.PropsWithChildren<{ label: string }>
> = ({ label, children }) => (
  <div
    data-panel="true"
    style={{
      position: "absolute",
      left: 852,
      top: 350,
      width: 940,
      height: 500,
      border: `1px solid ${d.line}`,
      borderRadius: 14,
      background: d.surface,
      boxShadow: "0 24px 72px #00000020",
    }}
  >
    <div
      style={{
        position: "absolute",
        left: 28,
        top: 20,
        right: 28,
        fontSize: 22,
        letterSpacing: 1,
        color: d.muted,
      }}
    >
      {label}
    </div>
    {children}
  </div>
);
export const Cursor: React.FC<{
  x: number;
  y: number;
  at: number;
  fromX?: number;
  fromY?: number;
}> = ({ x, y, at, fromX = 760, fromY = 420 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: interpolate(f, [(at - 0.7) * fps, at * fps], [fromX, x], ease),
        top: interpolate(f, [(at - 0.7) * fps, at * fps], [fromY, y], ease),
        opacity: interpolate(
          f,
          [
            (at - 0.9) * fps,
            (at - 0.7) * fps,
            (at + 0.5) * fps,
            (at + 1) * fps,
          ],
          [0, 1, 1, 0],
          clamp,
        ),
        zIndex: 10,
        pointerEvents: "none",
      }}
    >
      <svg width="42" height="48" viewBox="0 0 42 48" aria-hidden="true">
        <path
          d="M4 2L31 27H19L13 40Z"
          fill={d.ink}
          stroke={d.background}
          strokeWidth="2"
        />
      </svg>
      <div
        style={{
          position: "absolute",
          left: -16,
          top: -16,
          width: 44,
          height: 44,
          border: `2px solid ${d.mint}`,
          borderRadius: "50%",
          scale: interpolate(f, [at * fps, (at + 0.4) * fps], [0.2, 1.4], ease),
          opacity: interpolate(
            f,
            [at * fps, (at + 0.4) * fps],
            [0.65, 0],
            clamp,
          ),
        }}
      />
    </div>
  );
};
export const StepIndicator: React.FC<{ current: number; total: number }> = ({
  current,
  total,
}) => (
  <div
    style={{
      position: "absolute",
      left: 128,
      right: 128,
      bottom: 132,
      display: "flex",
      alignItems: "center",
      gap: 10,
    }}
  >
    {Array.from({ length: total }, (_, i) => (
      <span
        key={i}
        style={{
          width: i === current ? 64 : 24,
          height: 3,
          background: i <= current ? d.lavender : d.line,
        }}
      />
    ))}
    <span style={{ fontSize: 22, color: d.muted, marginLeft: 14 }}>
      ШАГ {current + 1} / {total}
    </span>
  </div>
);
export const FrameChrome: React.FC<{ number: string; title: string }> = ({
  number,
  title,
}) => {
  const f = useCurrentFrame();
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
        <svg width="30" height="30" viewBox="0 0 30 30">
          <path
            d="M2 23L15 2L28 23ZM8 23L15 11L22 23"
            fill="none"
            stroke={d.lavender}
            strokeWidth="2"
          />
        </svg>
        <span style={{ fontWeight: 700, color: d.ink, letterSpacing: 2 }}>
          AI COURSES
        </span>
        <span style={{ marginLeft: 18 }}>УРОК 113</span>
      </div>
      <div
        style={{ position: "absolute", right: 128, top: 67, letterSpacing: 1 }}
      >
        {number} / {title}
      </div>
      <div
        data-disclaimer="true"
        style={{ position: "absolute", left: 128, bottom: 70 }}
      >
        Схема интерфейса · не запись CapCut
      </div>
      <div style={{ position: "absolute", right: 128, bottom: 70 }}>
        Ф1 · ВЫМЫШЛЕННЫЙ УЧЕБНЫЙ ПРИМЕР
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
            width: `${interpolate(f, [0, durationInFrames - 1], [0, 100])}%`,
            background: d.lavender,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
