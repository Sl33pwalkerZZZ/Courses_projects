import { Composition, registerRoot } from "remotion";
import { Workspace } from "./Workspace";
registerRoot(() => (
  <>
    <Composition
      id="RoughCutQualityV2"
      component={Workspace}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1620}
      defaultProps={{ videoId: "rough-cut" }}
    />
    <Composition
      id="NarrationBalanceQualityV2"
      component={Workspace}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1800}
      defaultProps={{ videoId: "narration-balance" }}
    />
    <Composition
      id="CaptionReviewQualityV2"
      component={Workspace}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1800}
      defaultProps={{ videoId: "caption-review" }}
    />
  </>
));
