import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { design as d } from "../tokens";
import "../fonts";
import data from "../../content/quality-v2/series.json";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const images = ["Лист", "Проверка", "Схема", "Заметка", "Итог"];
const sourceNames = [
  "f1-paper-approved.png",
  "f1-notepad.png",
  "f1-voice-v01.wav",
];
export type SeriesProps = { videoId: string };

const Thumb = ({ index, large = false }: { index: number; large?: boolean }) =>
  index === 0 ? (
    <Img
      src={staticFile("f1/f1-paper-diagram.svg")}
      style={{ width: "100%", height: "100%", objectFit: "contain" }}
    />
  ) : (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background:
          index === 1 ? "#a6cfbc19" : index === 2 ? "#9ebacc19" : "#b7a6e819",
        color: d.ink,
        fontSize: large ? 26 : 17,
        textAlign: "center",
        padding: 4,
      }}
    >
      {images[index]}
      {large && (
        <span style={{ fontSize: 20, marginLeft: 18, color: d.muted }}>
          Учебный эскиз
        </span>
      )}
    </div>
  );

const Timeline = ({
  count,
  first,
  playhead,
  tracksFocus,
}: {
  count: number;
  first: number;
  playhead: number;
  tracksFocus: boolean;
}) => {
  const widths = [first, 8, 10, 10, 10];
  let start = 0;
  return (
    <div
      data-timeline="true"
      style={{
        position: "absolute",
        left: 20,
        top: 354,
        width: 950,
        height: 174,
        borderTop: `1px solid ${d.line}`,
      }}
    >
      <div
        data-read="true"
        style={{
          fontSize: 18,
          color: d.muted,
          position: "absolute",
          left: 0,
          top: 8,
        }}
      >
        ТАЙМЛАЙН
      </div>
      <div
        style={{
          position: "absolute",
          left: 108,
          top: 8,
          width: 820,
          height: 140,
        }}
      >
        {[0, 7, 15, 25, 35, 45].map((n) => (
          <span
            data-read="true"
            key={n}
            style={{
              position: "absolute",
              left: (n / 45) * 820 - (n === 45 ? 40 : 0),
              fontSize: 18,
              whiteSpace: "nowrap",
              color: d.muted,
            }}
          >
            {n} с
          </span>
        ))}
        {widths.slice(0, count).map((seconds, i) => {
          const x = (start / 45) * 820;
          start += seconds;
          return (
            <div
              data-clip={images[i]}
              key={images[i]}
              style={{
                position: "absolute",
                left: x,
                top: 35,
                width: (seconds / 45) * 820,
                height: 54,
                border: `1px solid ${d.line}`,
                background: i === 0 ? "#b7a6e82a" : "#16181c",
                overflow: "hidden",
              }}
            >
              <div style={{ height: 25, margin: 2 }}>
                <Thumb index={i} />
              </div>
              <div
                data-read="true"
                style={{
                  fontSize: 17,
                  textAlign: "center",
                  whiteSpace: "nowrap",
                }}
              >
                {images[i]}
                {i === 0 ? ` · ${first.toFixed(0)} с` : ""}
              </div>
            </div>
          );
        })}
        {!count && (
          <div
            data-read="true"
            style={{
              position: "absolute",
              left: 12,
              top: 47,
              color: d.muted,
              fontSize: 23,
            }}
          >
            Пока нет клипов
          </div>
        )}
        <div
          data-read="true"
          style={{
            position: "absolute",
            left: 0,
            top: 100,
            width: 820,
            height: 38,
            border: `1px solid ${tracksFocus ? d.lavender : d.line}`,
            borderRadius: 4,
            padding: "6px 10px",
            fontSize: 19,
            color: d.muted,
          }}
        >
          Аудиодорожка: запись ещё не размещена
        </div>
        {count > 0 && (
          <div
            data-playhead="true"
            style={{
              position: "absolute",
              left: (playhead / 45) * 820,
              top: 27,
              height: 65,
              width: 2,
              background: d.mint,
            }}
          />
        )}
      </div>
      <div
        data-read="true"
        style={{
          position: "absolute",
          left: 0,
          top: 55,
          fontSize: 19,
          color: d.muted,
        }}
      >
        ВИДЕО
      </div>
      <div
        data-read="true"
        style={{
          position: "absolute",
          left: 0,
          top: 115,
          fontSize: 19,
          color: d.muted,
        }}
      >
        АУДИО
      </div>
      <div
        data-read="true"
        style={{
          position: "absolute",
          left: 108,
          top: 149,
          fontSize: 19,
          color: d.muted,
        }}
      >
        {count > 1
          ? `Черновая сборка: ${(first + 38).toFixed(0)} с`
          : "Первый клип — черновик, ритм уточним позже"}
      </div>
    </div>
  );
};

export const SeriesWorkspace = ({ videoId }: SeriesProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const video = data.find((v) => v.id === videoId);
  if (!video) throw new Error("Unknown series video");
  let start = 0,
    index = video.scenes.length - 1;
  for (let i = 0; i < video.scenes.length; i++) {
    if (frame < (start + video.scenes[i].seconds) * fps) {
      index = i;
      break;
    }
    start += video.scenes[i].seconds;
  }
  const scene = video.scenes[index];
  const local = (frame - start * fps) / fps;
  const v2 = videoId === "project-import";
  const inList = v2
    ? index === 0 && local < 2.1
    : index === 4 && local >= 2 && local < 4.2;
  const imported = v2 ? index >= 3 || (index === 2 && local >= 2.1) : true;
  const selectedPaper = v2 ? index >= 3 || (index === 2 && local >= 4.5) : true;
  const first = v2
    ? 5
    : index < 2
      ? 5
      : index === 2
        ? interpolate(local, [0.9, 2.1], [5, 7], clamp)
        : 7;
  const count = v2
    ? index >= 4 || (index === 3 && local >= 2.1)
      ? 1
      : 0
    : index === 0 && local < 2.1
      ? 1
      : 5;
  const missing = !v2 && index === 5 && local >= 1.2 && local < 6.2;
  const wide = v2 ? (index === 4 ? local >= 2.1 : index >= 5) : true;
  const tracksFocus = !v2 && index === 1;
  const boundary = !v2 && index === 3;
  const playhead = boundary ? interpolate(local, [1, 4], [5.5, 8.5], clamp) : 2;
  const previewIndex = boundary && playhead >= 7 ? 1 : 0;
  const showPicture = selectedPaper && (!v2 || index !== 2 || local >= 4.5);
  return (
    <AbsoluteFill
      className="quality-series"
      style={{ fontFamily: d.font, background: d.background, color: d.ink }}
    >
      <style>{`.quality-series,.quality-series *{box-sizing:border-box}`}</style>
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
        <span>
          {video.number} /{" "}
          {v2 ? "Проект и импорт" : "Таймлайн и повторное открытие"}
        </span>
      </header>
      <h1
        data-read="true"
        style={{
          position: "absolute",
          left: 128,
          top: 174,
          width: 1664,
          margin: 0,
          fontSize: 76,
          fontWeight: 700,
          letterSpacing: -2.6,
          lineHeight: 1.15,
          opacity: interpolate(local, [0, 0.2], [0.45, 1], clamp),
        }}
      >
        {scene.title}
      </h1>
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
        <p
          data-read="true"
          style={{
            fontSize: 24,
            color: d.mint,
            lineHeight: 1.5,
            marginTop: 50,
          }}
        >
          {!v2 && index === 5
            ? "Условный пример ошибки, не задание переместить файлы."
            : !v2 && index === 4
              ? "Схема принципа, не подтверждение сохранения в CapCut."
              : "Имена файлов и интерфейс — учебные примеры."}
        </p>
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
          }}
        >
          F1_horizontal_v01{" "}
          <span style={{ color: d.muted, fontSize: 21 }}>
            {" "}
            · редактируемый проект
          </span>
        </div>
        {inList ? (
          <div style={{ position: "absolute", left: 30, right: 30, top: 110 }}>
            <p data-read="true" style={{ fontSize: 27, color: d.muted }}>
              {v2
                ? "Обычный проект, без готового шаблона"
                : "Сначала — штатное сохранение, затем список проектов"}
            </p>
            <div
              style={{ padding: 28, background: d.background, borderRadius: 8 }}
            >
              <strong data-read="true" style={{ fontSize: 32 }}>
                F1_horizontal_v01
              </strong>
              <p data-read="true" style={{ fontSize: 26, color: d.mint }}>
                {v2 ? "Создать и открыть" : "Открыть тот же проект"}
              </p>
            </div>
            <p
              data-read="true"
              style={{ fontSize: 24, color: d.muted, lineHeight: 1.5 }}
            >
              Конкретную команду проверьте в своей версии.
              <br />
              Облачная синхронизация не подразумевается.
            </p>
          </div>
        ) : (
          <>
            <div
              style={{
                position: "absolute",
                left: 20,
                top: 86,
                width: 260,
                height: 256,
              }}
            >
              <div
                data-read="true"
                style={{ fontSize: 22, color: d.muted, marginBottom: 8 }}
              >
                {v2 && index === 2 && !imported
                  ? "НА ДИСКЕ / F1_video"
                  : "БИБЛИОТЕКА"}
              </div>
              {imported || (v2 && index === 2) ? (
                sourceNames.map((name, i) => (
                  <div
                    data-read="true"
                    key={name}
                    style={{
                      padding: "6px 8px",
                      fontSize: 22,
                      lineHeight: 1.2,
                      marginBottom: 6,
                      borderRadius: 6,
                      color: missing && i === 0 ? d.sand : d.ink,
                      background: (
                        tracksFocus ? i === 2 : selectedPaper && i === 0
                      )
                        ? "#b7a6e825"
                        : "#16181c",
                      overflowWrap: "anywhere",
                    }}
                  >
                    {name}
                    <span
                      style={{
                        display: "block",
                        fontSize: 20,
                        color: d.muted,
                        marginTop: 3,
                      }}
                    >
                      {missing && i === 0
                        ? "Файл не найден"
                        : i === 2
                          ? "Озвучка · вне дорожки"
                          : i === 0
                            ? "Лист"
                            : "Блокнот"}
                    </span>
                  </div>
                ))
              ) : (
                <div
                  data-read="true"
                  style={{ fontSize: 25, color: d.muted, lineHeight: 1.55 }}
                >
                  Пока пусто.
                  <br />
                  {index === 1
                    ? "Здесь выбирают материал."
                    : "Исходники — отдельно."}
                </div>
              )}
            </div>
            <div
              style={{
                position: "absolute",
                left: 302,
                top: 86,
                width: 660,
                height: 244,
              }}
            >
              <div
                data-read="true"
                style={{ fontSize: 22, color: d.muted, marginBottom: 10 }}
              >
                ПРЕДПРОСМОТР{" "}
                {v2 && index === 2 && imported && !selectedPaper
                  ? " · выберите изображение"
                  : ""}
              </div>
              {v2 && index === 5 ? (
                <div style={{ fontSize: 24, lineHeight: 1.5 }}>
                  <p data-read="true" style={{ margin: "0 0 15px" }}>
                    Исходник: <strong>f1-paper-approved.png</strong>
                  </p>
                  <p data-read="true" style={{ margin: "0 0 15px" }}>
                    Проект: <strong>F1_horizontal_v01</strong>
                  </p>
                  <p data-read="true" style={{ margin: 0, color: d.muted }}>
                    Будущий экспорт: F1_horizontal_v01.mp4
                    <br />
                    <span style={{ color: d.sand }}>Ещё не создан</span>
                  </p>
                </div>
              ) : (
                <>
                  <div
                    data-preview="true"
                    style={{
                      height: 190,
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                      border: `1px solid ${d.line}`,
                      borderRadius: 7,
                      background: d.background,
                    }}
                  >
                    {missing ? (
                      <div
                        data-read="true"
                        style={{
                          textAlign: "center",
                          fontSize: 27,
                          color: d.sand,
                        }}
                      >
                        Материал недоступен
                        <br />
                        <span style={{ fontSize: 21 }}>
                          Укажите f1-paper-approved.png
                        </span>
                      </div>
                    ) : showPicture ? (
                      <div
                        data-canvas="true"
                        style={{
                          width: wide ? 304 : 228,
                          height: 171,
                          position: "relative",
                          background: "#242831",
                        }}
                      >
                        <Thumb index={previewIndex} large />
                        <span
                          data-read="true"
                          style={{
                            position: "absolute",
                            bottom: 0,
                            left: 0,
                            right: 0,
                            textAlign: "center",
                            fontSize: 18,
                            background: d.background + "e8",
                          }}
                        >
                          Учебный пример ·{" "}
                          {wide ? "16:9" : "формат ещё не выбран"}
                        </span>
                      </div>
                    ) : (
                      <div
                        data-read="true"
                        style={{
                          fontSize: 25,
                          color: d.muted,
                          textAlign: "center",
                        }}
                      >
                        {v2 && index === 1
                          ? "Здесь проверяют текущий кадр."
                          : "Изображение не выбрано"}
                      </div>
                    )}
                  </div>
                  {!v2 && index === 4 && local < 2 && (
                    <p
                      data-read="true"
                      style={{ margin: "6px 0", fontSize: 20, color: d.sand }}
                    >
                      Проверьте сохранение в установленной версии
                    </p>
                  )}
                  {!v2 && index === 5 && local >= 6.2 && (
                    <p
                      data-read="true"
                      style={{ margin: "6px 0", fontSize: 20, color: d.mint }}
                    >
                      Правильный исходник найден: проверьте изображение
                    </p>
                  )}
                </>
              )}
            </div>
            <Timeline
              count={count}
              first={first}
              playhead={playhead}
              tracksFocus={tracksFocus}
            />
          </>
        )}
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
          Шаг {index + 1} / {video.scenes.length} · Схема, не запись CapCut
        </span>
        <span>Ф1 — вымышленный учебный пример</span>
      </footer>
    </AbsoluteFill>
  );
};
