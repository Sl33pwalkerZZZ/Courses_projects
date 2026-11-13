import {
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { design as d } from "./tokens";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
type Kind = string;

const Card: React.FC<{
  title: string;
  detail: string;
  accent?: string;
  width?: number;
  delay?: number;
}> = ({ title, detail, accent = d.lavender, width = 390, delay = 0 }) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        width,
        minHeight: 142,
        padding: "24px 26px",
        borderRadius: 13,
        border: `1px solid ${d.line}`,
        borderLeft: `4px solid ${accent}`,
        background: d.background,
        opacity: interpolate(frame, [delay, delay + 16], [0, 1], clamp),
        transform: `translateY(${interpolate(frame, [delay, delay + 16], [20, 0], clamp)}px)`,
      }}
    >
      <div style={{ fontSize: 22, color: d.muted, marginBottom: 12 }}>{title}</div>
      <div style={{ fontSize: 29, color: d.ink, fontWeight: 700, lineHeight: 1.25 }}>{detail}</div>
    </div>
  );
};

const Flow: React.FC<{ steps: string[]; active: number }> = ({ steps, active }) => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 16, width: "100%" }}>
    {steps.map((step, i) => (
      <div key={step} style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ border: `1px solid ${i <= active ? d.mint : d.line}`, color: i <= active ? d.ink : d.muted, background: i <= active ? `${d.mint}18` : d.background, borderRadius: 12, padding: "22px 20px", minWidth: 170, textAlign: "center", fontSize: 23, lineHeight: 1.3, whiteSpace: "pre-line" }}>
          <div style={{ color: i <= active ? d.mint : d.muted, fontSize: 17, marginBottom: 9 }}>0{i + 1}</div>
          {step}
        </div>
        {i < steps.length - 1 && <div style={{ width: 35, height: 1, background: d.line }} />}
      </div>
    ))}
  </div>
);

const RatioFrame: React.FC<{ vertical: boolean; focus?: boolean }> = ({ vertical, focus = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const w = vertical ? 230 : 390;
  const h = vertical ? 410 : 220;
  return (
    <div style={{ width: w, height: h, position: "relative", border: `2px solid ${focus ? d.mint : d.line}`, borderRadius: 12, overflow: "hidden", background: d.background, opacity: interpolate(frame, [0, 18], [0, 1], clamp), transform: `scale(${interpolate(frame, [0, fps * 0.7], [0.96, 1], clamp)})` }}>
      <div style={{ position: "absolute", inset: "14% 12%", border: `1px solid ${d.sand}`, display: "grid", placeItems: "center", color: d.ink, fontSize: 21, textAlign: "center", padding: 12, background: `${d.sand}12` }}>Объект и важная подпись</div>
      <div style={{ position: "absolute", left: 10, top: 9, color: d.muted, fontSize: 16 }}>{vertical ? "9:16" : "16:9"}</div>
    </div>
  );
};

const FolderTree = () => (
  <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
    <div style={{ border: `1px solid ${d.line}`, borderRadius: 12, padding: 25, width: 280, color: d.ink, fontSize: 26, background: d.background }}>
      <div style={{ color: d.sand, marginBottom: 18, fontSize: 18 }}>ПРОЕКТ</div>F1_video
      <div style={{ marginTop: 18, color: d.muted, fontSize: 20 }}>исходная версия</div>
    </div>
    <div style={{ color: d.mint, fontSize: 44 }}>→</div>
    <div style={{ border: `1px solid ${d.line}`, borderRadius: 12, padding: 25, width: 350, color: d.ink, fontSize: 25, background: d.background }}>
      <div style={{ color: d.mint, marginBottom: 18, fontSize: 18 }}>ОТДЕЛЬНАЯ ВЕРСИЯ</div>
      <div style={{ padding: 12, background: `${d.lavender}18`, borderRadius: 7 }}>F1_vertical</div>
      <div style={{ marginTop: 15, color: d.muted, fontSize: 19 }}>горизонтальный исходник сохранён</div>
    </div>
  </div>
);

const RightsChecklist = () => (
  <div style={{ width: "100%", display: "grid", gridTemplateColumns: "1fr 230px", fontSize: 22, borderTop: `1px solid ${d.line}` }}>
    {["Изображения", "Голос", "Музыка", "Шрифты"].map((item) => (
      <div key={item} style={{ display: "contents" }}>
        <div style={{ borderBottom: `1px solid ${d.line}`, padding: "16px 20px", color: d.ink }}>{item}</div>
        <div style={{ borderBottom: `1px solid ${d.line}`, padding: "16px 20px", color: d.sand, textAlign: "right" }}>Проверить</div>
      </div>
    ))}
  </div>
);

const ClaimReview = () => (
  <div style={{ display: "flex", alignItems: "center", gap: 35 }}>
    <div style={{ border: `1px solid ${d.line}`, background: d.background, padding: 30, borderRadius: 12, width: 500 }}>
      <div style={{ fontSize: 18, color: d.sand, marginBottom: 17 }}>УЧЕБНЫЙ КОНТРПРИМЕР</div>
      <div style={{ fontSize: 33, color: d.ink, lineHeight: 1.3 }}>«Проект экономит ресурсы»</div>
      <div style={{ color: d.muted, fontSize: 21, marginTop: 15 }}>источник или расчёт не указан</div>
    </div>
    <div style={{ color: d.muted, fontSize: 40 }}>→</div>
    <div style={{ border: `1px solid ${d.mint}70`, background: `${d.mint}10`, padding: 28, borderRadius: 12, width: 300, textAlign: "center", color: d.mint, fontSize: 25 }}>Убрать до проверки</div>
  </div>
);

const renderVisual = (kind: Kind, local: number) => {
  switch (kind) {
    case "project-file":
      return <Flow steps={["Проект\nдля монтажа", "Экспортированный\nфайл", "Проверка\nрезультата"]} active={Math.min(2, Math.floor(local / 80))} />;
    case "file-name":
      return <div style={{ display: "flex", gap: 20 }}><Card title="ПАПКА" detail="exports/" accent={d.sand} width={290} /><Card title="ПРИМЕР ИМЕНИ" detail="f1-horizontal-v01.mp4" accent={d.lavender} width={380} /><Card title="ОТДЕЛЬНО" detail="проект + исходники" accent={d.mint} width={290} /></div>;
    case "container-codec":
      return <div style={{ width: 720, border: `1px solid ${d.blue}`, padding: 28, borderRadius: 12, background: `${d.blue}0c` }}><div style={{ color: d.blue, fontSize: 18, marginBottom: 20 }}>КОНТЕЙНЕР · ПРИМЕР MP4</div><div style={{ display: "flex", gap: 20 }}><Card title="Видеопоток" detail="H.264" accent={d.lavender} width={315} /><Card title="Аудиопоток" detail="AAC" accent={d.mint} width={315} /></div><div style={{ color: d.muted, fontSize: 19, marginTop: 20 }}>Свойства проверяют в готовом файле; доступные параметры зависят от проекта и версии.</div></div>;
    case "export-flow":
      return <Flow steps={["Подготовка", "Кодирование", "Файл сохранён"]} active={Math.min(2, Math.floor(local / 90))} />;
    case "player-check":
      return <div style={{ display: "flex", alignItems: "center", gap: 20 }}><div style={{ width: 560, height: 315, border: `1px solid ${d.line}`, background: d.background, borderRadius: 12, display: "grid", placeItems: "center" }}><div style={{ width: 320, height: 180, border: `1px solid ${d.sand}`, borderRadius: 8, display: "grid", placeItems: "center", color: d.ink, fontSize: 22 }}>Иллюстрация кадра</div></div><div style={{ display: "grid", gap: 12 }}><Card title="ПРОВЕРИТЬ" detail="начало" width={240} /><Card title="ПРОВЕРИТЬ" detail="середину и конец" width={300} /></div></div>;
    case "metadata-check":
      return <div style={{ border: `1px solid ${d.line}`, padding: 28, background: d.background, borderRadius: 12, width: 750, fontFamily: "monospace", fontSize: 22, lineHeight: 1.7, color: d.ink }}><div style={{ color: d.muted }}>Пример команды · путь замените своим</div><div style={{ color: d.mint, marginTop: 17 }}>ffprobe -show_streams -show_format файл.mp4</div><div style={{ marginTop: 20, color: d.muted }}>Затем сверить фактические:</div><div>codec · width / height · frame rate</div><div>audio stream · duration</div><div style={{ color: d.sand, marginTop: 16 }}>Результат не показан и не измерялся.</div></div>;
    case "separate-version":
      return <FolderTree />;
    case "aspect-ratio":
      return <div style={{ display: "flex", alignItems: "center", gap: 35 }}><RatioFrame vertical={false} /><div style={{ color: d.mint, fontSize: 42 }}>→</div><RatioFrame vertical focus /></div>;
    case "reframe":
      return <div style={{ display: "flex", gap: 30, alignItems: "center" }}><RatioFrame vertical={false} /><div style={{ color: d.muted, fontSize: 38 }}>→</div><RatioFrame vertical focus /></div>;
    case "text-safe":
      return <div style={{ width: 500, height: 340, border: `2px solid ${d.line}`, borderRadius: 12, position: "relative", background: d.background }}><div style={{ position: "absolute", inset: 22, border: `1px dashed ${d.mint}`, display: "grid", placeItems: "center", color: d.ink, fontSize: 24, textAlign: "center", padding: 30 }}>Объект остаётся видимым<br/><br/><span style={{ color: d.sand, fontSize: 18 }}>Вымышленный учебный пример · Ф1</span></div><div style={{ position: "absolute", bottom: 30, left: 0, right: 0, textAlign: "center", color: d.muted, fontSize: 16 }}>Условная зона размещения текста</div></div>;
    case "scene-review":
      return <div style={{ display: "flex", gap: 20 }}>{["Начало", "Середина", "Конец"].map((t, i) => <div key={t}><RatioFrame vertical focus={i === Math.floor(local / 90) % 3} /><div style={{ textAlign: "center", marginTop: 12, color: d.muted, fontSize: 19 }}>{t}</div></div>)}</div>;
    case "compare-ratios":
      return <div style={{ display: "flex", alignItems: "center", gap: 26 }}><RatioFrame vertical={false} /><div style={{ color: d.mint, fontSize: 34 }}>СМЫСЛ<br/>сохранён?</div><RatioFrame vertical focus /></div>;
    case "version-identity":
      return <div style={{ display: "flex", gap: 20 }}><Card title="ФАЙЛ" detail="версия 01" accent={d.lavender} width={290} /><Card title="ТЕХНИКА" detail="изображение · звук" accent={d.blue} width={290} /><Card title="СОДЕРЖАНИЕ" detail="факты · права" accent={d.sand} width={290} /></div>;
    case "playback-check":
      return <div style={{ display: "grid", gap: 22, width: 730 }}><div style={{ border: `1px solid ${d.line}`, borderRadius: 12, height: 250, background: d.background, display: "grid", placeItems: "center", color: d.ink, fontSize: 24 }}>Схематичный просмотр видеокадра</div><Flow steps={["Начало", "Середина", "Конец"]} active={Math.min(2, Math.floor(local / 80))} /></div>;
    case "claim-review":
      return <ClaimReview />;
    case "rights-check":
      return <div style={{ width: 680 }}><RightsChecklist /></div>;
    case "caption-check":
      return <div style={{ width: 650, border: `1px solid ${d.line}`, borderRadius: 12, padding: 28, background: d.background }}><div style={{ color: d.muted, fontSize: 18, marginBottom: 22 }}>ПРОВЕРКА ЧИТАЕМОСТИ</div><div style={{ color: d.ink, fontSize: 31, lineHeight: 1.35 }}>Смысл и важные оговорки понятны без звука.</div><div style={{ marginTop: 23, height: 9, background: d.line, borderRadius: 6 }}><div style={{ width: `${Math.round(interpolate(local, [0, 150], [12, 82], clamp))}%`, height: 9, background: d.mint, borderRadius: 6 }} /></div></div>;
    case "handoff":
      return <Flow steps={["Файл", "Заметка о проверках", "Редактор"]} active={Math.min(2, Math.floor(local / 100))} />;
    default:
      return <Card title="УЧЕБНАЯ СХЕМА" detail="Проверяйте фактический результат" />;
  }
};

export const SceneVisual: React.FC<{ kind: Kind }> = ({ kind }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = interpolate(frame, [0, fps * 0.55], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", left: 20, right: 20, top: 70, bottom: 5, display: "flex", alignItems: "center", justifyContent: "center", opacity: enter, transform: `translateY(${interpolate(frame, [0, fps * 0.55], [14, 0], clamp)}px)` }}>
      {renderVisual(kind, frame)}
    </div>
  );
};
