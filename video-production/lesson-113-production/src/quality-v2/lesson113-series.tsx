import { Composition, registerRoot } from "remotion";
import { SeriesWorkspace } from "./SeriesWorkspace";
const SeriesRoot = () => (
  <>
    <Composition
      id="ProjectImportQualityV2"
      component={SeriesWorkspace}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1410}
      defaultProps={{ videoId: "project-import" }}
    />
    <Composition
      id="TimelineReopenQualityV2"
      component={SeriesWorkspace}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1620}
      defaultProps={{ videoId: "timeline-reopen" }}
    />
  </>
);
registerRoot(SeriesRoot);
