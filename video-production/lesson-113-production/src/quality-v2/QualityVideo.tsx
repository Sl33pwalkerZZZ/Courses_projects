import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { design as d } from "../tokens";
import "../fonts";
import scenes from "../../content/quality-v2/video-1.json";

const folders = [
  ["sources", "Изображения и записи"],
  ["audio", "Озвучка и звук"],
  ["captions", "Субтитры"],
  ["exports", "Готовые версии"],
  ["notes", "Бриф, план и права"],
];
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const FileRow = ({
  name,
  label,
  active = false,
}: {
  name: string;
  label: string;
  active?: boolean;
}) => (
  <div
    data-read="true"
    style={{
      padding: "15px 18px",
      borderRadius: 8,
      background: active ? "#b7a6e815" : "#16181c",
      marginBottom: 12,
    }}
  >
    <div
      style={{ fontSize: 25, color: active ? d.ink : d.muted, fontWeight: 600 }}
    >
      {name}
    </div>
    <div style={{ fontSize: 22, color: d.muted, marginTop: 5 }}>{label}</div>
  </div>
);
const CheckRow = ({ children }: { children: React.ReactNode }) => (
  <div
    data-read="true"
    style={{ fontSize: 26, margin: "18px 0", lineHeight: 1.4 }}
  >
    <span
      aria-hidden="true"
      style={{
        display: "inline-block",
        width: 15,
        height: 15,
        border: `1px solid ${d.muted}`,
        marginRight: 16,
      }}
    />
    {children}
  </div>
);

export const QualityVideo = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  let start = 0;
  let index = scenes.length - 1;
  for (let i = 0; i < scenes.length; i++) {
    if (f < (start + scenes[i].seconds) * fps) {
      index = i;
      break;
    }
    start += scenes[i].seconds;
  }
  const scene = scenes[index];
  const local = f - start * fps;
  const copied = local >= 2.1 * fps;
  const selected = local >= 2.1 * fps;
  // The workspace stays mounted at exactly the same coordinates for all 46s.
  return (
    <AbsoluteFill
      className="quality-v2"
      style={{ fontFamily: d.font, background: d.background, color: d.ink }}
    >
      <style>{`.quality-v2,.quality-v2 *{box-sizing:border-box}`}</style>
      <header
        style={{
          position: "absolute",
          left: 128,
          right: 128,
          top: 66,
          display: "flex",
          justifyContent: "space-between",
          fontSize: 24,
          color: d.muted,
        }}
      >
        <span>
          <strong style={{ color: d.ink, letterSpacing: 1, marginRight: 24 }}>
            AI COURSES
          </strong>
          УРОК 113
        </span>
        <span>01 / Подготовка исходников</span>
      </header>
      <div
        style={{
          position: "absolute",
          left: 128,
          top: 174,
          width: 1664,
          opacity: interpolate(local, [0, 0.2 * fps], [0.45, 1], clamp),
        }}
      >
        <h1
          data-read="true"
          style={{
            margin: 0,
            fontSize: 76,
            fontWeight: 700,
            letterSpacing: -2.6,
            lineHeight: 1.15,
          }}
        >
          {scene.title}
        </h1>
      </div>
      <aside style={{ position: "absolute", left: 128, top: 352, width: 600 }}>
        <p
          data-read="true"
          style={{ fontSize: 41, fontWeight: 700, lineHeight: 1.3, margin: 0 }}
        >
          {scene.instruction}
        </p>
        <p
          data-read="true"
          style={{
            fontSize: 29,
            color: d.muted,
            lineHeight: 1.55,
            marginTop: 32,
          }}
        >
          {scene.note}
        </p>
        <div
          data-read="true"
          style={{
            fontSize: 24,
            color: index === 5 && local < 6 * fps ? d.muted : d.mint,
            marginTop: 50,
            lineHeight: 1.5,
          }}
        >
          {index === 0
            ? "Ф1 — вымышленный учебный проект."
            : index === 5
              ? "Дальше: создать проект и импортировать проверенные материалы."
              : "Имена файлов показаны как учебные примеры."}
        </div>
      </aside>
      <section
        data-workspace="true"
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
          data-read="true"
          style={{
            height: 67,
            padding: "21px 26px",
            fontSize: 25,
            borderBottom: `1px solid ${d.line}`,
            color: d.ink,
          }}
        >
          F1_video{scene.folder !== "root" ? ` / ${scene.folder}` : ""}
        </div>
        <nav
          aria-label="Рабочие папки"
          style={{ position: "absolute", left: 16, top: 85, width: 228 }}
        >
          <div
            data-read="true"
            style={{ fontSize: 22, color: d.muted, padding: "0 10px 16px" }}
          >
            РАБОЧАЯ ПАПКА
          </div>
          {folders.map(([name]) => (
            <div
              data-folder={name}
              data-read="true"
              key={name}
              style={{
                fontSize: 26,
                padding: "14px 12px",
                marginBottom: 6,
                borderRadius: 7,
                color: scene.folder === name ? d.ink : d.muted,
                background: scene.folder === name ? "#b7a6e820" : "transparent",
              }}
            >
              <span
                aria-hidden="true"
                style={{
                  display: "inline-block",
                  width: 19,
                  height: 14,
                  border: `1px solid ${d.sand}`,
                  borderRadius: 2,
                  marginRight: 13,
                }}
              />
              {name}
            </div>
          ))}
        </nav>
        <main
          style={{
            position: "absolute",
            left: 270,
            top: 88,
            width: 690,
            height: 426,
          }}
        >
          {index === 0 && (
            <>
              <div
                data-read="true"
                style={{ fontSize: 29, fontWeight: 600, marginBottom: 24 }}
              >
                «Вторая сторона листа»
              </div>
              <FileRow
                name="F1_video"
                label="Отдельный набор рабочих материалов"
                active
              />
              <FileRow
                name="Оригиналы — отдельно"
                label="Копируем выбранное, не перемещаем исходники"
              />
              <p
                data-read="true"
                style={{ fontSize: 24, lineHeight: 1.5, color: d.muted }}
              >
                Учебная схема. Реальные результаты
                <br />и расчёт экономии не заявляются.
              </p>
            </>
          )}
          {index === 1 && (
            <>
              <div
                data-read="true"
                style={{ fontSize: 27, fontWeight: 600, marginBottom: 18 }}
              >
                Назначение папок
              </div>
              {folders.map(([name, purpose]) => (
                <div
                  key={name}
                  data-read="true"
                  style={{
                    display: "grid",
                    gridTemplateColumns: "165px 1fr",
                    fontSize: 26,
                    padding: "12px 0",
                    borderRadius: 6,
                    background:
                      name === "sources" && local >= 1.2 * fps
                        ? "#b7a6e815"
                        : "transparent",
                    lineHeight: 1.3,
                  }}
                >
                  <span style={{ color: d.sand }}>{name}</span>
                  <span>{purpose}</span>
                </div>
              ))}
            </>
          )}
          {index === 2 && (
            <>
              <div
                data-read="true"
                style={{ fontSize: 25, color: d.muted, marginBottom: 13 }}
              >
                Рабочие копии / sources
              </div>
              <div
                style={{
                  opacity: 1,
                }}
              >
                <FileRow
                  name={
                    copied ? "f1-paper-approved.png" : "Копия изображения листа"
                  }
                  label={
                    copied
                      ? "Понятное имя после проверки содержимого"
                      : "Выбранный материал"
                  }
                  active
                />
                <FileRow
                  name={
                    copied ? "f1-notepad.png" : "Копия изображения блокнота"
                  }
                  label="Второй рабочий файл"
                />
              </div>
              <div
                style={{
                  padding: "12px 18px",
                  border: `1px solid ${d.line}`,
                  borderRadius: 8,
                }}
              >
                <div
                  data-read="true"
                  style={{ fontSize: 24, color: d.sand, marginBottom: 7 }}
                >
                  Оригиналы — отдельно, без изменений
                </div>
                <div data-read="true" style={{ fontSize: 23, color: d.muted }}>
                  Изображение листа · Изображение блокнота
                </div>
              </div>
            </>
          )}
          {index === 3 && (
            <>
              <FileRow
                name="f1-paper-approved.png"
                label="Та же рабочая копия: имя не подтверждает права"
                active
              />
              <div data-read="true" style={{ fontSize: 25, lineHeight: 1.65 }}>
                Автор: <span style={{ color: d.muted }}>указать</span>
                <br />
                Источник:{" "}
                <span style={{ color: d.muted }}>записать ссылку или файл</span>
                <br />
                Условия:{" "}
                <span style={{ color: d.muted }}>
                  проверить распространение
                </span>
              </div>
              <p
                data-read="true"
                style={{
                  fontSize: 24,
                  lineHeight: 1.45,
                  color: d.sand,
                  marginBottom: 0,
                }}
              >
                Шаблон проверки, не разрешение.
                <br />
                Неясные права — не импортировать.
              </p>
            </>
          )}
          {index === 4 && (
            <>
              <FileRow
                name="f1-voice-v01.wav"
                label={
                  selected
                    ? "Выбранная согласованная версия"
                    : "Сравните версии перед выбором"
                }
                active={selected}
              />
              <FileRow
                name="f1-voice-test.wav"
                label="Эксперимент — не выбирать для импорта"
              />
              <p
                data-read="true"
                style={{ fontSize: 24, lineHeight: 1.5, color: d.muted }}
              >
                Сохраните текст, происхождение и права.
                <br />В captions проверьте текст и тайминг SRT.
              </p>
            </>
          )}
          {index === 5 && (
            <>
              <div
                data-read="true"
                style={{ fontSize: 27, fontWeight: 600, marginBottom: 18 }}
              >
                Что проверить до импорта
              </div>
              <CheckRow>Рабочие копии: понятные имена</CheckRow>
              <CheckRow>Для каждого файла: источник и права</CheckRow>
              <CheckRow>Озвучка и подписи: нужные версии</CheckRow>
              <CheckRow>В notes: бриф, кадровый план, права</CheckRow>
              <p
                data-read="true"
                style={{ fontSize: 23, color: d.muted, marginTop: 26 }}
              >
                Проект и готовое видео ещё не создавались.
              </p>
            </>
          )}
        </main>
      </section>
      <footer
        style={{
          position: "absolute",
          left: 128,
          right: 128,
          bottom: 50,
          display: "flex",
          justifyContent: "space-between",
          fontSize: 24,
          color: d.muted,
        }}
      >
        <span data-read="true">
          Шаг {index + 1} / 6 · Схема, не запись CapCut
        </span>
        <span>Ф1 — вымышленный учебный пример</span>
      </footer>
    </AbsoluteFill>
  );
};
