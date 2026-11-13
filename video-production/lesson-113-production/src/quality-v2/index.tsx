import { Composition, registerRoot } from "remotion";
import { QualityVideo } from "./QualityVideo";
const QualityRoot = () => (
  <Composition
    id="SourceOrganizationQualityV2"
    component={QualityVideo}
    durationInFrames={1380}
    fps={30}
    width={1920}
    height={1080}
  />
);
registerRoot(QualityRoot);
