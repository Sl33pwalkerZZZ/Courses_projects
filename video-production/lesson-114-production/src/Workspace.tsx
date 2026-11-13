import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { design as d } from "../../lesson-113-production/src/tokens";
import "../../lesson-113-production/src/fonts";
import videos from "../content/series.json";
import speech from "../content/speech.json";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const spoken = speech.transcript;
export type Props = { videoId: string };
const Text = ({
  children,
  size = 24,
  color = d.ink,
}: {
  children: React.ReactNode;
  size?: number;
  color?: string;
}) => (
  <div data-read style={{ fontSize: size, color, lineHeight: 1.35 }}>
    {children}
  </div>
);
const Wave = ({ width = 580 }: { width?: number }) => (
  <svg width={width} height={36} aria-label="Волна из настоящей записи Ф1">
    <g stroke={d.mint} strokeWidth={3}>
      {speech.waveform_rms.map((v, i) => (
        <line
          key={i}
          x1={(i * width) / 120}
          x2={(i * width) / 120}
          y1={18 - Math.min(17, v * 130)}
          y2={18 + Math.min(17, v * 130)}
        />
      ))}
    </g>
  </svg>
);
const bar = (
  left: number,
  width: number,
  label: string,
  color: string,
  top: number,
) => (
  <div
    key={label}
    style={{
      position: "absolute",
      left,
      top,
      width,
      height: 50,
      background: color + "28",
      border: `1px solid ${color}`,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: 21,
      whiteSpace: "nowrap",
    }}
    data-read
  >
    {label}
  </div>
);
const labels = ["Лист", "Проверка", "Сборка", "Блокнот"];
function Rough({ index, local }: { index: number; local: number }) {
  const imported = index > 0 || local >= 2;
  const trim =
    index === 1
      ? interpolate(local, [1, 3], [12, 10], clamp)
      : index > 1
        ? 10
        : 12;
  const split = index > 2 || (index === 2 && local >= 2);
  const secondSplit = index > 2 || (index === 2 && local >= 4);
  const deleted = index > 3 || (index === 3 && local >= 2);
  const closed =
    index >= 5
      ? 1
      : index === 4
        ? interpolate(local, [1, 3], [0, 1], clamp)
        : 0;
  const still = index >= 5;
  const first = index === 5 ? interpolate(local, [4, 6], [5, 7], clamp) : 7;
  const reorder = index === 5 ? interpolate(local, [1, 3], [0, 1], clamp) : 1;
  const cursor =
    index === 6 ? interpolate(local, [1, 5], [5.5, 8.5], clamp) : 2;
  const widths = [first, 5, 5, 5];
  let acc = 0;
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: 22,
          right: 22,
          top: 74,
          display: "flex",
          gap: 24,
        }}
      >
        <div
          style={{
            width: 288,
            background: d.background,
            padding: 14,
            borderRadius: 8,
          }}
        >
          <Text size={20} color={d.muted}>
            БИБЛИОТЕКА Ф1
          </Text>
          <Text size={23}>
            {still
              ? "Схемы Ф1: лист, проверка, сборка, блокнот"
              : imported
                ? "demo-action.mp4"
                : "Выбранный пример"}
          </Text>
          <Text size={20} color={d.mint}>
            {still ? "Не видеосъёмка" : "Условная запись действия"}
          </Text>
        </div>
        <div
          style={{
            flex: 1,
            background: d.background,
            padding: 14,
            borderRadius: 8,
            minHeight: 132,
          }}
        >
          <Text size={20} color={d.muted}>
            ПРЕДПРОСМОТР · НЕ СЪЁМКА
          </Text>
          <Text size={28}>
            {still
              ? cursor < first
                ? "Лист: учебная схема"
                : "Проверка бумаги"
              : index === 0
                ? "Импорт → библиотека → таймлайн"
                : deleted
                  ? "Действие продолжается"
                  : "Действие · пауза · действие"}
          </Text>
          <Text size={21} color={d.muted}>
            {still
              ? "Важная подпись сохранена"
              : "Разделение на дорожке не изменяет исходник."}
          </Text>
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 22,
          right: 22,
          top: 250,
          height: 240,
          borderTop: `1px solid ${d.line}`,
        }}
      >
        <Text size={20} color={d.muted}>
          ВИДЕО · {still ? "КАРТИНКИ Ф1" : "СХЕМА ВРЕМЕННОЙ ЗАПИСИ"}
        </Text>
        <div
          style={{
            position: "absolute",
            left: 100,
            top: 40,
            width: 830,
            height: 100,
          }}
        >
          {[0, 3, 5, 10, 15, 22].map((n) => (
            <div
              key={n}
              data-read
              style={{
                position: "absolute",
                left: (n / 22) * 830 - (n === 22 ? 34 : 0),
                top: 0,
                fontSize: 19,
                whiteSpace: "nowrap",
              }}
            >
              {n}с
            </div>
          ))}
          {!imported ? (
            <Text color={d.muted}>Пока нет клипов</Text>
          ) : still ? (
            labels.map((label, i) => {
              const original = [0, 3, 1, 2][i];
              const left = interpolate(
                reorder,
                [0, 1],
                [original * 190, (acc / 22) * 830],
                clamp,
              );
              acc += widths[i];
              return bar(
                left,
                (widths[i] / 22) * 830 - 3,
                label,
                d.lavender,
                40,
              );
            })
          ) : !split ? (
            bar(
              0,
              (trim / 22) * 830,
              `Действие · ${Math.round(trim)}с`,
              d.lavender,
              40,
            )
          ) : (
            <>
              {bar(0, (3 / 22) * 830, "Начало", d.lavender, 40)}
              {!deleted &&
                bar(
                  (3 / 22) * 830,
                  ((secondSplit ? 2 : trim - 3) / 22) * 830,
                  secondSplit ? "Пауза" : "Остальное",
                  secondSplit ? d.sand : d.lavender,
                  40,
                )}
              {secondSplit &&
                bar(
                  ((5 - 2 * closed) / 22) * 830,
                  (5 / 22) * 830,
                  "Продолжение",
                  d.lavender,
                  40,
                )}
              {deleted && closed < 1 && (
                <div
                  style={{
                    position: "absolute",
                    left: (3 / 22) * 830,
                    top: 98,
                    fontSize: 20,
                    color: d.sand,
                  }}
                  data-read
                >
                  Разрыв 2с
                </div>
              )}
            </>
          )}
          {index === 6 && (
            <div
              style={{
                position: "absolute",
                left: (cursor / 22) * 830,
                top: 30,
                height: 70,
                borderLeft: `3px solid ${d.mint}`,
              }}
            />
          )}
        </div>
        <div style={{ position: "absolute", top: 170 }}>
          <Text size={23} color={d.muted}>
            {still
              ? `Лист: ${Math.round(first)}с · порядок по смыслу`
              : deleted
                ? closed === 1
                  ? "Разрыв закрыт вручную · итог 8с"
                  : "Удалена только середина · исходник сохранён"
                : secondSplit
                  ? "ВЫБРАНО: пауза 3–5с · соседние части сохраняются"
                  : `Исходник 12с · выбранный фрагмент ${Math.round(trim)}с`}
          </Text>
        </div>
      </div>
    </>
  );
}
function projectTime(index: number, local: number, caption = false) {
  const start = caption ? (index === 1 ? 1 : 0) : index === 2 ? 0.5 : 1;
  return Math.max(0, Math.min(speech.seconds, local - start));
}
function AudioWorkspace({ index, local }: { index: number; local: number }) {
  const placed = index > 1 || (index === 1 && local >= 1);
  const t = projectTime(index, local);
  const listening = [2, 3, 5].includes(index);
  const phase =
    index === 2
      ? "ГОЛОС БЕЗ МУЗЫКИ"
      : index === 3
        ? "A · ФОН КОНКУРИРУЕТ"
        : index === 5
          ? "B · ТИХИЙ ФОН"
          : "ПРОВЕРКА ИСТОЧНИКА";
  const caption =
    speech.captions.find((c) => t * 1000 >= c.startMs && t * 1000 < c.endMs)
      ?.text || "";
  const level =
    index === 2
      ? 0
      : index === 3
        ? 1
        : index === 4
          ? interpolate(local, [1, 3], [1, 0.25], clamp)
          : 0.25;
  return (
    <>
      <div style={{ position: "absolute", left: 22, right: 22, top: 74 }}>
        <Text size={20} color={d.mint}>
          {phase}
        </Text>
        <Text size={24}>
          {listening ? caption || "Пауза исходной записи" : spoken}
        </Text>
        <Text size={20} color={d.muted}>
          m4-l11-silero-ru-roman-approved.wav · 8,5625с · Silero MIT
        </Text>
      </div>
      <div
        style={{
          position: "absolute",
          left: 22,
          right: 22,
          top: 246,
          height: 250,
          borderTop: `1px solid ${d.line}`,
        }}
      >
        {["ВИДЕО", "ГОЛОС", "МУЗЫКА"].map((x, i) => (
          <div
            key={x}
            data-read
            style={{
              position: "absolute",
              top: 48 + i * 62,
              fontSize: 20,
              color: d.muted,
            }}
          >
            {x}
          </div>
        ))}
        <div style={{ position: "absolute", left: 112, top: 14, width: 810 }}>
          {[0, 3, 6, 9].map((v) => (
            <span
              data-read
              key={v}
              style={{
                position: "absolute",
                left: (v / 10) * 800,
                fontSize: 19,
              }}
            >
              {v}с
            </span>
          ))}
          {bar(0, (3.25 / 10) * 800, "Лист", d.lavender, 30)}
          {bar(
            (3.25 / 10) * 800,
            ((8.5625 - 3.25) / 10) * 800,
            "Блокнот · до конца реплики",
            d.lavender,
            30,
          )}
          {placed && (
            <div
              style={{
                position: "absolute",
                top: 92,
                width: (8.5625 / 10) * 800,
                height: 50,
                background: d.mint + "19",
                border: `1px solid ${d.mint}`,
                padding: "6px 8px",
              }}
            >
              <Wave width={665} />
            </div>
          )}
          <div
            style={{
              position: "absolute",
              top: 154,
              width: (8.5625 / 10) * 800,
              height: 50,
              background: d.blue + "22",
              border: `1px solid ${d.blue}`,
              padding: 10,
            }}
          >
            <div
              style={{
                height: 24,
                width: `${level * 100}%`,
                background: d.blue,
                opacity: 0.65,
              }}
            />
          </div>
          {listening && (
            <div
              style={{
                position: "absolute",
                left: (t / 10) * 800,
                top: 28,
                height: 180,
                borderLeft: `3px solid ${d.ink}`,
              }}
            />
          )}
        </div>
      </div>
      <div style={{ position: "absolute", left: 22, right: 22, bottom: 20 }}>
        <Text size={20} color={d.muted}>
          {index === 6
            ? "Мягкий край музыки · слова не обрезаны"
            : "Громкость голоса в A и B одинакова · волна из реального WAV"}
        </Text>
      </div>
    </>
  );
}
function Captions({ index, local }: { index: number; local: number }) {
  const t = projectTime(index, local, true);
  const replay = index === 1 || index === 6;
  const cue =
    speech.captions.find((c) => t * 1000 >= c.startMs && t * 1000 < c.endMs)
      ?.text || "Пауза записи";
  const fixed = index > 3 || (index === 3 && local >= 2);
  const punctuation = index > 3 || (index === 3 && local >= 4.5);
  const timing =
    index >= 5
      ? 1
      : index === 4
        ? interpolate(local, [1.2, 3.2], [0, 1], clamp)
        : 1;
  return (
    <>
      <div style={{ position: "absolute", left: 22, right: 22, top: 72 }}>
        <Text size={20} color={d.sand}>
          СМОДЕЛИРОВАННЫЙ ПРИМЕР · ASR НЕ ЗАПУСКАЛАСЬ
        </Text>
        <Text size={24} color={d.muted}>
          Эталон: «а не измерение экономии»
        </Text>
      </div>
      {index === 5 ? (
        <div
          style={{
            position: "absolute",
            left: 22,
            right: 22,
            top: 170,
            display: "flex",
            gap: 20,
          }}
        >
          <div
            style={{
              flex: 1,
              padding: 20,
              background: d.background,
              borderRadius: 8,
            }}
          >
            <Text size={27}>SRT · в редактор</Text>
            <pre
              data-read
              style={{ fontSize: 19, lineHeight: 1.6, whiteSpace: "pre-wrap" }}
            >
              {"1\n00:00:06,425 --> 00:00:08,312\nа не измерение экономии."}
            </pre>
          </div>
          <div
            style={{
              flex: 1,
              padding: 20,
              background: d.background,
              borderRadius: 8,
            }}
          >
            <Text size={27}>WebVTT · в плеер</Text>
            <pre
              data-read
              style={{ fontSize: 19, lineHeight: 1.6, whiteSpace: "pre-wrap" }}
            >
              {
                "WEBVTT\n\n00:00:06.425 --> 00:00:08.312\nа не измерение экономии."
              }
            </pre>
          </div>
        </div>
      ) : (
        <>
          <div
            style={{
              position: "absolute",
              left: 22,
              right: 22,
              top: 170,
              padding: 22,
              background: d.background,
              minHeight: 120,
              borderRadius: 8,
              border: `1px solid ${index === 2 ? d.sand : d.line}`,
            }}
          >
            <Text size={29}>
              {replay
                ? cue
                : index === 0
                  ? "Речь → черновой текст → проверка человеком"
                  : index === 2
                    ? "Это пример повторного использования бумаги а измерение экономии"
                    : index === 3
                      ? `Это пример повторного использования бумаги${punctuation ? "," : ""} а ${fixed ? "не " : ""}измерение экономии${punctuation ? "." : ""}`
                      : "а не измерение экономии."}
            </Text>
          </div>
          <div style={{ position: "absolute", left: 22, right: 22, top: 330 }}>
            <Wave width={900} />
            <div
              style={{
                height: 64,
                position: "relative",
                borderTop: `1px solid ${d.line}`,
                marginTop: 10,
              }}
            >
              {[0, 3, 6, 9].map((x) => (
                <span
                  data-read
                  key={x}
                  style={{
                    position: "absolute",
                    left: (x / 9) * 860,
                    fontSize: 20,
                  }}
                >
                  {x}с
                </span>
              ))}
              <div
                style={{
                  position: "absolute",
                  left: ((5.8 + (6.425 - 5.8) * timing) / 9) * 860,
                  top: 30,
                  width: ((1.7 + (1.887 - 1.7) * timing) / 9) * 860,
                  height: 30,
                  background: d.mint + "55",
                  border: `1px solid ${d.mint}`,
                }}
              />
              {replay && (
                <div
                  style={{
                    position: "absolute",
                    left: (t / 9) * 860,
                    top: -43,
                    height: 102,
                    borderLeft: `3px solid ${d.ink}`,
                  }}
                />
              )}
            </div>
            <Text size={21} color={d.muted}>
              {index === 4
                ? timing === 1
                  ? "Исправлено: 6,425–8,312с"
                  : "Пример ошибки времени: 5,8–7,5с"
                : "Точные границы из существующей синтезированной записи"}
            </Text>
          </div>
        </>
      )}
    </>
  );
}
export function Workspace({ videoId }: Props) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const video = videos.find((v) => v.id === videoId)!;
  let offset = 0;
  let index = video.scenes.length - 1;
  for (let i = 0; i < video.scenes.length; i++) {
    if (frame < (offset + video.scenes[i].seconds) * fps) {
      index = i;
      break;
    }
    offset += video.scenes[i].seconds;
  }
  const scene = video.scenes[index];
  const local = (frame - offset * fps) / fps;
  return (
    <AbsoluteFill
      style={{ background: d.background, fontFamily: d.font, color: d.ink }}
    >
      <style>{`*{box-sizing:border-box}body{margin:0}`}</style>
      <header
        style={{
          position: "absolute",
          left: 128,
          right: 128,
          top: 65,
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <Text size={24}>
          AI COURSES <span style={{ color: d.muted }}>УРОК 114</span>
        </Text>
        <Text size={24} color={d.muted}>
          {videoId === "rough-cut"
            ? "04 / Черновой монтаж"
            : videoId === "narration-balance"
              ? "05 / Озвучка и баланс"
              : "06 / Проверка субтитров"}
        </Text>
      </header>
      <div
        style={{
          position: "absolute",
          left: 128,
          right: 128,
          top: 174,
          fontWeight: 700,
          fontSize: 64,
          lineHeight: 1.15,
          opacity: interpolate(local, [0, 0.22], [0.45, 1], clamp),
        }}
        data-read
      >
        {scene.title}
      </div>
      <aside style={{ position: "absolute", left: 128, top: 352, width: 600 }}>
        <Text size={35}>{scene.instruction}</Text>
        <div style={{ marginTop: 28 }}>
          <Text size={27} color={d.muted}>
            {scene.note}
          </Text>
        </div>
        <div style={{ marginTop: 44 }}>
          <Text size={22} color={d.mint}>
            Ф1 — вымышленный учебный пример.
          </Text>
        </div>
      </aside>
      <section
        style={{
          position: "absolute",
          left: 800,
          top: 340,
          width: 992,
          height: 550,
          border: `1px solid ${d.line}`,
          borderRadius: 14,
          background: d.surface,
        }}
      >
        <div
          style={{ padding: "16px 22px", borderBottom: `1px solid ${d.line}` }}
        >
          <Text size={24}>
            F1_horizontal_v01{" "}
            <span style={{ color: d.muted }}>· учебная копия проекта</span>
          </Text>
        </div>
        {videoId === "rough-cut" ? (
          <Rough index={index} local={local} />
        ) : videoId === "narration-balance" ? (
          <AudioWorkspace index={index} local={local} />
        ) : (
          <Captions index={index} local={local} />
        )}
      </section>
      <footer
        style={{
          position: "absolute",
          left: 128,
          right: 128,
          bottom: 48,
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <Text size={23} color={d.muted}>
          Шаг {index + 1} / {video.scenes.length} · Схема, не запись CapCut
        </Text>
        <Text size={22} color={d.muted}>
          Имена и элементы интерфейса — иллюстрация
        </Text>
      </footer>
    </AbsoluteFill>
  );
}
