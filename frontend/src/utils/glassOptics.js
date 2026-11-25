// Original, static edge-normal map. Neutral centre leaves text behind the lens stable.
export function createRefractionPixels(size = 128) {
  const data = new Uint8ClampedArray(size * size * 4)
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const nx = (x + .5) / size * 2 - 1, ny = (y + .5) / size * 2 - 1
    const distance = Math.hypot(nx, ny) || 1
    const edge = Math.max(0, (Math.max(Math.abs(nx), Math.abs(ny)) - .68) / .32) ** 2
    const i = (y * size + x) * 4
    data[i] = 128 + nx / distance * edge * 110
    data[i + 1] = 128 + ny / distance * edge * 110
    data[i + 2] = 128
    data[i + 3] = 255
  }
  return data
}

// A visual enhancement allowlist, never an authorization/capability decision.
// CSS.supports(url(...)) alone accepts syntax even when the browser cannot render it.
export function allowSvgOptics({ userAgent = '', cores = 8, mobile = false, reduced = false }) {
  return !mobile && !reduced && cores > 4 && /(?:Chrome|Chromium|Edg)\//.test(userAgent) && !/Firefox|OPR\//.test(userAgent)
}
