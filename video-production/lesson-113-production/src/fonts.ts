import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const fontReady = Promise.all([
  loadFont({
    family: "Studio Noto",
    url: staticFile("fonts/NotoSans-Regular.ttf"),
    weight: "400",
  }),
  loadFont({
    family: "Studio Noto",
    url: staticFile("fonts/NotoSans-Bold.ttf"),
    weight: "700",
  }),
]);
