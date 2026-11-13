export const design = {
  background: "#16181c",
  surface: "#20232a",
  line: "#383c46",
  ink: "#f3f0e9",
  muted: "#a4a7b1",
  lavender: "#b7a6e8",
  mint: "#a6cfbc",
  blue: "#9ebacc",
  sand: "#d9c8a7",
  font: "Studio Noto",
  safeX: 128,
} as const;

// Approved prototype easing intervals; production scene durations live in content/videos.json.
export const timing = {
  entrance: 0.8,
  organizeStart: 2.8,
  organizeEnd: 4.65,
  transformStart: 7.8,
  transformEnd: 9.05,
} as const;
