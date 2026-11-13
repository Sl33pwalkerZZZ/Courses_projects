import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { design as d } from "./tokens";
import { clamp, Cursor, ease, Label, Paper } from "./primitives";

const folders = [
  ["sources", "Изображения и записи"],
  ["audio", "Звук"],
  ["captions", "Подписи"],
  ["exports", "Готовые версии"],
  ["notes", "Бриф, план, права"],
];
const inset: React.CSSProperties = {
  position: "absolute",
  left: 30,
  right: 30,
  top: 82,
  bottom: 24,
};
export const FileCard: React.FC<{ name: string; notepad?: boolean }> = ({
  name,
  notepad = false,
}) => (
  <div
    style={{
      width: 288,
      border: `1px solid ${d.line}`,
      borderRadius: 10,
      padding: 18,
      background: d.background,
    }}
  >
    <Paper notepad={notepad} width={250} height={180} />
    <div
      data-read="true"
      style={{
        fontSize: 23,
        color: d.ink,
        marginTop: 12,
        overflowWrap: "anywhere",
      }}
    >
      {name}
    </div>
  </div>
);
export const FolderExplorer: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={inset}>
      <div
        data-read="true"
        style={{
          fontSize: 40,
          fontWeight: 700,
          color: d.lavender,
          marginBottom: 18,
        }}
      >
        F1_video /
      </div>
      {folders.map(([name, label], i) => (
        <div
          key={name}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 22,
            padding: "12px 12px",
            borderBottom: `1px solid ${d.line}`,
            opacity: interpolate(
              f,
              [(at - 0.5 + i * 0.12) * fps, (at + i * 0.12) * fps],
              [0, 1],
              clamp,
            ),
            translate: interpolate(
              f,
              [(at - 0.5 + i * 0.12) * fps, (at + i * 0.12) * fps],
              ["24px 0px", "0px 0px"],
              ease,
            ),
          }}
        >
          <svg width="40" height="30" viewBox="0 0 40 30">
            <path
              d="M1 6H13L17 1H25V6H39V29H1Z"
              stroke={i === 3 ? d.sand : d.mint}
              fill="none"
            />
          </svg>
          <span
            data-read="true"
            style={{ fontSize: 29, width: 175, fontWeight: 700, color: d.ink }}
          >
            {name}
          </span>
          <span data-read="true" style={{ fontSize: 25, color: d.muted }}>
            {label}
          </span>
        </div>
      ))}
    </div>
  );
};
export const TimelineTracks: React.FC<{ mode: string; at: number }> = ({
  mode,
  at,
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = interpolate(f, [(at - 0.5) * fps, (at + 0.5) * fps], [0, 1], ease);
  const zoom =
    mode === "zoom"
      ? interpolate(f, [(at - 0.3) * fps, (at + 0.6) * fps], [1, 1.35], ease)
      : 1;
  const first =
    mode === "trim"
      ? interpolate(f, [(at - 0.55) * fps, at * fps], [5, 7], ease)
      : 7;
  const widths = [first, 8, 10, 10, 10];
  const starts = [0, 7, 15, 25, 35];
  return (
    <div style={inset}>
      <div
        data-read="true"
        style={{ fontSize: 27, color: d.muted, marginBottom: 24 }}
      >
        1 Лист · 2 Проверка · 3 Схема · 4 Заметка · 5 Итог
      </div>
      <div
        style={{
          height: 285,
          overflow: "hidden",
          position: "relative",
          border: `1px solid ${d.line}`,
          borderRadius: 8,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 22,
            top: 70,
            fontSize: 23,
            color: d.muted,
          }}
        >
          ВИДЕО
        </div>
        <div
          style={{
            position: "absolute",
            left: 22,
            top: 168,
            fontSize: 23,
            color: d.muted,
          }}
        >
          ЗВУК
        </div>
        <div
          style={{
            position: "absolute",
            left: 145,
            top: 10,
            width: 708 * zoom,
            height: 242,
          }}
        >
          <div
            style={{
              position: "relative",
              height: 30,
              color: d.muted,
              fontSize: 22,
            }}
          >
            {[0, 7, 15, 25, 35, 45]
              .filter((second) => (second / 45) * 708 * zoom <= 708)
              .map((second) => (
                <span
                  key={second}
                  style={{
                    position: "absolute",
                    left: (second / 45) * 708 * zoom,
                    translate: "-50% 0px",
                    whiteSpace: "nowrap",
                  }}
                >
                  {second === 0 ? "0" : `${second} с`}
                </span>
              ))}
          </div>
          {starts.map((start, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                left: (start / 45) * 708 * zoom,
                top: 52,
                width: (widths[i] / 45) * 708 * zoom,
                borderRight: `2px solid ${d.surface}`,
                height: 72,
                borderRadius: 5,
                background: i === 0 ? d.lavender : i === 4 ? d.sand : d.blue,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 29,
                fontWeight: 700,
                color: d.background,
                opacity: interpolate(
                  f,
                  [(0.35 + i * 0.12) * fps, (0.75 + i * 0.12) * fps],
                  [0, 1],
                  clamp,
                ),
              }}
            >
              {i + 1}
              {i === 0 && mode === "trim" ? (
                <span style={{ fontSize: 21, marginLeft: 8 }}>
                  {first.toFixed(0)} с
                </span>
              ) : null}
            </div>
          ))}
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 151,
              width: 705 * zoom,
              height: 47,
              borderRadius: 5,
              background: d.mint,
              opacity: 0.65,
            }}
          >
            <svg
              width="100%"
              height="47"
              viewBox="0 0 708 47"
              preserveAspectRatio="none"
            >
              <path
                d={Array.from(
                  { length: 155 },
                  (_, i) =>
                    `M${i * 4.5} ${23 - (5 + Math.sin(i * 0.71) ** 2 * 12)}v${10 + Math.sin(i * 0.71) ** 2 * 24}`,
                ).join(" ")}
                stroke={d.background}
                strokeWidth="2"
              />
            </svg>
          </div>
          <div
            style={{
              position: "absolute",
              top: 38,
              height: 180,
              width: 2,
              background: d.ink,
              left:
                ((mode === "cut"
                  ? 4 + 6 * p
                  : mode === "trim"
                    ? first
                    : 4 + 26 * p) /
                  45) *
                708 *
                zoom,
              zIndex: 3,
            }}
          >
            <div
              style={{
                width: 10,
                height: 10,
                rotate: "45deg",
                background: d.ink,
                marginLeft: -4,
              }}
            />
          </div>
        </div>
      </div>
      <div
        data-read="true"
        style={{
          fontSize: 24,
          color: mode === "zoom" ? d.mint : d.muted,
          marginTop: 18,
        }}
      >
        {mode === "zoom"
          ? "Масштаб 1× → 1.35× · длительность не меняется"
          : mode === "trim"
            ? "7 с — черновой ориентир, не стандарт"
            : "Звуковая дорожка показана условно; диктора здесь нет"}
      </div>
      {mode === "trim" && (
        <Cursor
          x={145 + (7 / 45) * 708}
          y={132}
          at={at}
          fromX={224}
          fromY={132}
        />
      )}
    </div>
  );
};
export const Workspace: React.FC<{ mode: string; at: number }> = ({
  mode,
  at,
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const active = interpolate(f, [at * fps, (at + 0.4) * fps], [0, 1], ease);
  return (
    <div style={inset}>
      <div style={{ display: "flex", gap: 18, height: 242 }}>
        <div
          style={{
            width: 265,
            border: `1px solid ${d.line}`,
            borderRadius: 8,
            padding: 16,
          }}
        >
          <Label>БИБЛИОТЕКА</Label>
          <div style={{ opacity: mode === "import" ? active : 1 }}>
            <Paper width={220} height={135} />
            <div data-read="true" style={{ fontSize: 22, color: d.muted }}>
              Изображение листа
            </div>
          </div>
        </div>
        <div
          style={{
            flex: 1,
            border: `1px solid ${d.line}`,
            borderRadius: 8,
            padding: 16,
          }}
        >
          <Label>ПРЕДПРОСМОТР</Label>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              opacity: mode === "place" ? active : 1,
            }}
          >
            <Paper width={235} height={155} />
            <div data-read="true" style={{ fontSize: 25, color: d.muted }}>
              Учебный
              <br />
              пример Ф1
            </div>
          </div>
        </div>
      </div>
      <div
        style={{
          marginTop: 18,
          border: `1px solid ${d.line}`,
          borderRadius: 8,
          padding: 16,
          height: 104,
        }}
      >
        <Label>ТАЙМЛАЙН</Label>
        <div
          style={{
            marginTop: 10,
            height: 34,
            width:
              mode === "import" ? 0 : mode === "place" ? 220 * active : 480,
            background: d.lavender,
            borderRadius: 4,
          }}
        />
      </div>
      {mode === "place" ? (
        <Cursor x={100} y={340} at={at} fromX={125} fromY={120} />
      ) : mode === "import" ? (
        <Cursor x={125} y={130} at={at} />
      ) : null}
    </div>
  );
};
const CheckRow: React.FC<{
  children: React.ReactNode;
  highlight?: boolean;
}> = ({ children, highlight = false }) => (
  <div
    data-read="true"
    style={{
      padding: "17px 18px",
      marginBottom: 12,
      border: `1px solid ${highlight ? d.mint : d.line}`,
      borderRadius: 8,
      fontSize: 28,
      color: highlight ? d.ink : d.muted,
      background: d.background,
    }}
  >
    {children}
  </div>
);

export const Visual: React.FC<{ kind: string; at: number }> = ({
  kind,
  at,
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const active = interpolate(f, [at * fps, (at + 0.45) * fps], [0, 1], ease);
  if (kind === "folders") return <FolderExplorer at={at} />;
  if (["timeline", "trim", "cut", "zoom"].includes(kind))
    return <TimelineTracks mode={kind} at={at} />;
  if (["workspace", "import", "place"].includes(kind))
    return <Workspace mode={kind} at={at} />;
  if (kind === "brief")
    return (
      <div
        style={{
          ...inset,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 35,
            scale: interpolate(
              f,
              [(at - 0.5) * fps, (at + 0.4) * fps],
              [0.92, 1],
              { ...ease, output: "perceptual-scale" },
            ),
          }}
        >
          <Paper width={290} height={230} />
          <Paper notepad width={290} height={230} />
        </div>
        <div
          data-read="true"
          style={{
            fontSize: 38,
            fontWeight: 700,
            color: d.lavender,
            marginTop: 22,
          }}
        >
          «Вторая сторона листа»
        </div>
        <Label>Оригинальные учебные схемы</Label>
      </div>
    );
  if (kind === "copies")
    return (
      <div style={inset}>
        <Label>Рабочие копии → F1_video / sources</Label>
        <div
          style={{
            display: "flex",
            gap: 26,
            justifyContent: "center",
            marginTop: 28,
            translate: interpolate(
              f,
              [(at - 0.65) * fps, at * fps],
              ["40px 0px", "0px 0px"],
              ease,
            ),
          }}
        >
          <FileCard name="f1-paper-approved.png" />
          <FileCard name="f1-notepad.png" notepad />
        </div>
        <div style={{ marginTop: 20 }}>
          <Label>Примеры имён · оригиналы храним отдельно</Label>
        </div>
      </div>
    );
  if (kind === "rights")
    return (
      <div style={inset}>
        <CheckRow>Автор → укажите создателя</CheckRow>
        <CheckRow>Источник → сохраните ссылку</CheckRow>
        <CheckRow highlight={active > 0.5}>
          Условия → проверьте распространение
        </CheckRow>
        <div style={{ fontSize: 25, color: d.sand, marginTop: 24 }}>
          Неясные права → не импортировать
        </div>
        <div style={{ fontSize: 22, color: d.muted, marginTop: 16 }}>
          Шаблон проверки, не документ разрешения
        </div>
        <Cursor x={690} y={193} at={at} />
      </div>
    );
  if (kind === "approved")
    return (
      <div style={inset}>
        <CheckRow highlight={active > 0.5}>
          Выбранная версия · проверить текст
        </CheckRow>
        <CheckRow>Сохранить происхождение и права</CheckRow>
        <CheckRow>Экспериментальный файл ≠ утверждённый</CheckRow>
        <div style={{ fontSize: 24, color: d.muted, marginTop: 30 }}>
          f1-voice-v01.wav — пример имени
        </div>
        <div style={{ fontSize: 24, color: d.muted, marginTop: 12 }}>
          Ни один голосовой файл здесь не воспроизводится
        </div>
        <Cursor x={730} y={35} at={at} />
      </div>
    );
  if (kind === "ready" || kind === "finish")
    return (
      <div style={inset}>
        <CheckRow highlight>Порядок сцен понятен</CheckRow>
        <CheckRow highlight>Права и версии проверены вами</CheckRow>
        <CheckRow highlight>Исходники доступны при открытии</CheckRow>
        <div
          data-read="true"
          style={{
            fontSize: 31,
            color: d.lavender,
            marginTop: 26,
            opacity: active,
          }}
        >
          Материал → проект → экспорт
        </div>
        <div style={{ fontSize: 23, color: d.muted, marginTop: 14 }}>
          Это список для вашей проверки, не отчёт программы
        </div>
      </div>
    );
  if (kind === "create")
    return (
      <div style={{ ...inset, textAlign: "center", paddingTop: 25 }}>
        <div style={{ fontSize: 70, fontWeight: 700, color: d.lavender }}>
          F1
        </div>
        <div
          data-read="true"
          style={{ fontSize: 38, color: d.ink, marginTop: 22, opacity: active }}
        >
          F1_horizontal_v01
        </div>
        <div
          style={{
            display: "inline-block",
            border: `1px solid ${d.lavender}`,
            padding: "16px 32px",
            borderRadius: 8,
            fontSize: 28,
            marginTop: 36,
            color: d.ink,
          }}
        >
          Новый проект
        </div>
        <div style={{ fontSize: 24, color: d.muted, marginTop: 32 }}>
          Схема действия, не расположение кнопки
        </div>
        <Cursor x={445} y={235} at={at} />
      </div>
    );
  if (kind === "ratio")
    return (
      <div style={inset}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 40,
            justifyContent: "center",
            height: 305,
          }}
        >
          <div
            style={{
              width: 480,
              height: 270,
              border: `2px solid ${active > 0.5 ? d.mint : d.line}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              position: "relative",
            }}
          >
            <Paper width={270} height={190} />
            <span
              style={{
                position: "absolute",
                left: 14,
                top: 12,
                fontSize: 24,
                color: d.mint,
              }}
            >
              16:9
            </span>
            <span
              style={{
                position: "absolute",
                left: 20,
                bottom: 8,
                fontSize: 22,
                color: d.muted,
              }}
            >
              Учебный пример
            </span>
          </div>
          <div
            style={{
              width: 155,
              height: 275,
              border: `1px solid ${d.line}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 28,
              color: d.muted,
            }}
          >
            9:16
          </div>
        </div>
        <Label>1920×1080 и 1280×720 — оба 16:9</Label>
        <div style={{ marginTop: 14 }}>
          <Label>Не растягивайте изображение по одной оси</Label>
        </div>
        <Cursor x={285} y={120} at={at} />
      </div>
    );
  if (kind === "entities")
    return (
      <div style={inset}>
        <div style={{ display: "flex", gap: 18, marginTop: 55 }}>
          {[
            ["Исходники", "Фото, схемы, звук", d.mint],
            ["Проект", "Редактируемая сборка", d.lavender],
            ["Экспорт", "MP4 для просмотра", d.sand],
          ].map(([title, text, color]) => (
            <div
              key={title}
              style={{
                flex: 1,
                border: `1px solid ${color}`,
                borderRadius: 12,
                padding: "28px 18px",
                height: 210,
              }}
            >
              <div
                data-read="true"
                style={{ fontSize: 31, fontWeight: 700, color }}
              >
                {title}
              </div>
              <div
                data-read="true"
                style={{
                  fontSize: 25,
                  color: d.muted,
                  marginTop: 32,
                  lineHeight: 1.4,
                }}
              >
                {text}
              </div>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 35 }}>
          <Label>Экспорт не заменяет проект и исходники</Label>
        </div>
      </div>
    );
  if (kind === "reopen")
    return (
      <div style={inset}>
        <div
          data-read="true"
          style={{ fontSize: 32, color: d.lavender, marginBottom: 24 }}
        >
          F1_horizontal_v01
        </div>
        <CheckRow highlight={active < 0.5}>
          Сверить сохранение со своей версией
        </CheckRow>
        <CheckRow highlight={active > 0.5}>
          Список проектов → открыть сборку
        </CheckRow>
        <CheckRow>Проверить порядок и длительности</CheckRow>
        <div style={{ fontSize: 23, color: d.muted, marginTop: 25 }}>
          Не обещаем автоматическую облачную копию
        </div>
        <Cursor x={730} y={185} at={at} />
      </div>
    );
  if (kind === "links")
    return (
      <div style={inset}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 20,
            marginTop: 40,
          }}
        >
          <div
            style={{
              border: `1px solid ${d.lavender}`,
              padding: 26,
              borderRadius: 10,
              width: 255,
            }}
          >
            <Label>КЛИП В ПРОЕКТЕ</Label>
            <Paper width={200} height={150} />
          </div>
          <div
            style={{
              height: 2,
              flex: 1,
              background: active > 0.5 ? d.mint : d.sand,
              position: "relative",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: -24,
                left: "35%",
                fontSize: 28,
                color: d.sand,
                opacity: 1 - active,
              }}
            >
              ?
            </div>
          </div>
          <div
            style={{
              border: `1px solid ${d.mint}`,
              padding: 26,
              borderRadius: 10,
              width: 325,
            }}
          >
            <div style={{ fontSize: 28, color: d.ink }}>F1_video / sources</div>
            <div style={{ fontSize: 24, color: d.muted, marginTop: 30 }}>
              Найти верный файл
            </div>
          </div>
        </div>
        <div style={{ marginTop: 38 }}>
          <Label>Способ поиска зависит от версии редактора</Label>
        </div>
        <Cursor x={705} y={195} at={at} />
      </div>
    );
  return null;
};
