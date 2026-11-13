import { Composition } from "remotion";
import { ProjectFilesPrototype } from "./Composition";

export const RemotionRoot = () => (
  <Composition
    id="Module5StyleTest"
    component={ProjectFilesPrototype}
    durationInFrames={360}
    fps={30}
    width={1920}
    height={1080}
  />
);
