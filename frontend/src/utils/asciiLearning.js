// Original sampled toroidal sculpture. No third-party animation or artwork.
export const ASCII_COLUMNS = 88
export const ASCII_ROWS = 48
const TAU = Math.PI * 2
const SHADES = '.,:;=+*#%@'
const samples = []
for (let ring = 0; ring < 160; ring += 1) {
  const u = ring / 160 * TAU
  for (let tube = 0; tube < 60; tube += 1) {
    const v = tube / 60 * TAU
    const radius = 1.48 + 0.48 * Math.cos(v)
    samples.push([radius * Math.cos(u), radius * Math.sin(u), 0.48 * Math.sin(v), Math.cos(v) * Math.cos(u), Math.cos(v) * Math.sin(u), Math.sin(v), u])
  }
}

export function createAsciiFrame(seconds = 0) {
  const time = Number.isFinite(seconds) ? seconds : 0
  const yaw = time * 0.23
  const tilt = 0.62 + Math.sin(time * 0.19) * 0.3
  const cy = Math.cos(yaw), sy = Math.sin(yaw), ct = Math.cos(tilt), st = Math.sin(tilt)
  const grid = Array.from({ length: ASCII_ROWS }, () => Array(ASCII_COLUMNS).fill(' '))
  const depths = new Float32Array(ASCII_COLUMNS * ASCII_ROWS).fill(-Infinity)
  for (const [x, y, z, nx, ny, nz, u] of samples) {
    const swell = 1 + 0.075 * Math.sin(u * 3 + time * 0.42)
    const a = x * cy + z * sy
    const b = -x * sy + z * cy
    const py = y * ct - b * st
    const pz = y * st + b * ct
    const perspective = 5.6 / (5.6 - pz * 0.45)
    const column = Math.round(ASCII_COLUMNS / 2 + a * swell * 18 * perspective)
    const row = Math.round(ASCII_ROWS / 2 + py * swell * 9.2 * perspective)
    if (column < 1 || column >= ASCII_COLUMNS - 1 || row < 1 || row >= ASCII_ROWS - 1) continue
    const index = row * ASCII_COLUMNS + column
    if (pz <= depths[index]) continue
    depths[index] = pz
    const normalX = nx * cy + nz * sy
    const normalZ = -nx * sy + nz * cy
    const normalY = ny * ct - normalZ * st
    const normalDepth = ny * st + normalZ * ct
    const light = Math.max(0, Math.min(1, 0.36 - normalX * 0.25 - normalY * 0.32 + normalDepth * 0.52))
    grid[row][column] = SHADES[Math.round(light * (SHADES.length - 1))]
  }
  return grid.map((row) => row.join('')).join('\n')
}
export const STATIC_ASCII_FRAME = createAsciiFrame(2.8)
