export default function SubjectGraphic({ seed = '' }) {
  const hash = [...seed].reduce((n, char) => (n * 31 + char.codePointAt(0)) >>> 0, 7)
  const points = Array.from({ length: 6 }, (_, i) => ({ x: 16 + ((hash >>> (i * 3)) % 168), y: 12 + ((hash >>> (i * 2 + 1)) % 65) }))
  return <svg className="play-subject-graphic" viewBox="0 0 200 92" aria-hidden="true" focusable="false">
    <path d={points.map((p, i) => `${i ? 'L' : 'M'}${p.x} ${p.y}`).join(' ')} />
    {points.map((p, i) => <g key={i}><circle cx={p.x} cy={p.y} r={i === 2 ? 9 : 4} /><circle cx={p.x} cy={p.y} r={i === 2 ? 16 : 8} className="play-subject-halo" /></g>)}
  </svg>
}
