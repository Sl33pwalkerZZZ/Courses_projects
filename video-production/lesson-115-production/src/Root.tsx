import { Composition } from "remotion";
import { Lesson115, calculateMetadata } from "./Lesson115";

export const RemotionRoot = () => (
  <>
    <Composition
      id="ExportCheck"
      component={Lesson115}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={3600}
      calculateMetadata={calculateMetadata}
      defaultProps={{ videoId: "m5-l15-v1-export-check" }}
    />
    <Composition
      id="VerticalAdaptation"
      component={Lesson115}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={3450}
      calculateMetadata={calculateMetadata}
      defaultProps={{ videoId: "m5-l15-v2-vertical-adaptation" }}
    />
    <Composition
      id="FinalReview"
      component={Lesson115}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={3450}
      calculateMetadata={calculateMetadata}
      defaultProps={{ videoId: "m5-l15-v3-final-review" }}
    />
  </>
);
