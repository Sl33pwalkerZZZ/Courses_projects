// Original deterministic interference field: directional currents bend one another.
// Small raster, no assets, random particles, WebGL, filters or external code.
export const LIQUID_QUALITY = Object.freeze({ desktop: { width: 160, height: 100, fps: 24 }, mobile: { width: 96, height: 72, fps: 12 } })
const clamp = value => Math.max(0, Math.min(1, value))
export function createLiquidPixels(width, height, time, dark = false, output = new Uint8ClampedArray(width * height * 4)) {
  const base = dark ? [11, 16, 23] : [238, 242, 245]
  const depth = dark ? [20, 52, 69] : [166, 195, 213]
  const light = dark ? [62, 132, 142] : [199, 229, 230]
  const drift = time * .16
  for (let y = 0; y < height; y++) {
    const v = y / height
    for (let x = 0; x < width; x++) {
      const u = x / width
      const bend = Math.sin(v * 5.2 + drift) * .32 + Math.sin(u * 4.3 - drift * .73) * .18
      const current = Math.sin((u * 1.25 + v * .6 + bend) * 5.7 - drift * 1.2)
      const crossing = Math.sin((v * 1.8 - u * .55 + current * .18) * 4.2 + drift * .8)
      const field = clamp(.5 + current * .29 + crossing * .21)
      // Narrow highlights are formed by the field itself rather than overlaid circles.
      const crest = Math.pow(clamp(1 - Math.abs(current * .76 + crossing * .24)), 14)
      const mix = .15 + field * .67
      const sheen = crest * (dark ? .38 : .55)
      const i = (y * width + x) * 4
      for (let c = 0; c < 3; c++) {
        const submerged = base[c] + (depth[c] - base[c]) * mix
        output[i + c] = submerged + (light[c] - submerged) * sheen
      }
      output[i + 3] = 255
    }
  }
  return output
}
