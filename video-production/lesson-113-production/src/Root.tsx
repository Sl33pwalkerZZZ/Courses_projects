import { Composition } from "remotion";
import { Tutorial, calculateTutorialMetadata } from "./Tutorial";

export const RemotionRoot = () => (
  <>
    <Composition
      id="SourceOrganization"
      component={Tutorial}
      calculateMetadata={calculateTutorialMetadata}
      durationInFrames={1380}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        videoId: "source-organization",
        sfxVolume: 0.4,
        muteSfx: false,
      }}
    />
    <Composition
      id="ProjectImport"
      component={Tutorial}
      calculateMetadata={calculateTutorialMetadata}
      durationInFrames={1410}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        videoId: "project-import",
        sfxVolume: 0.4,
        muteSfx: false,
      }}
    />
    <Composition
      id="TimelineReopen"
      component={Tutorial}
      calculateMetadata={calculateTutorialMetadata}
      durationInFrames={1620}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        videoId: "timeline-reopen",
        sfxVolume: 0.4,
        muteSfx: false,
      }}
    />
  </>
);
