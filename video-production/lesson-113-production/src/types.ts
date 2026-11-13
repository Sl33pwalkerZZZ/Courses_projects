export type Scene = {
  id: string;
  seconds: number;
  title: string;
  instruction: string;
  note: string;
  visual: string;
  sfx: string;
  actionAt: number;
  alternative: string;
  detail: string;
};
export type TutorialData = {
  id: string;
  composition: string;
  filename: string;
  title: string;
  number: string;
  anchor: string;
  seconds: number;
  scenes: Scene[];
};
export type Cue = {
  frame: number;
  duration: number;
  sound: string;
  gain: number;
  scene: string;
};
