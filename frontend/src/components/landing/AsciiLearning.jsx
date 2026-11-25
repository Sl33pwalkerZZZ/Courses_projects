import { useEffect, useRef } from 'react'
import { useMediaQuery, useReducedMotion } from '../../hooks/useMotionPreferences'
import { ASCII_COLUMNS, ASCII_ROWS, STATIC_ASCII_FRAME, createAsciiFrame } from '../../utils/asciiLearning'
import './AsciiLearning.css'

export default function AsciiLearning() {
  const hostRef = useRef(null)
  const canvasRef = useRef(null)
  const mobile = useMediaQuery('(max-width: 767px)', true)
  const reducedMotion = useReducedMotion()
  const staticMode = reducedMotion

  useEffect(() => {
    const host = hostRef.current
    const canvas = canvasRef.current
    if (!host || !canvas || staticMode) return
    const context = canvas.getContext('2d')
    if (!context) return
    let frame = 0
    let visible = true
    let disposed = false
    let draws = 0
    let lastDraw = 0
    let elapsed = 0
    let previousTime = 0
    let color = getComputedStyle(host).color
    const lowPower = mobile || (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4)
    const interval = 1000 / (lowPower ? 20 : 30)
    const draw = (now) => {
      frame = 0
      if (disposed || !visible || document.hidden) return
      const bounds = host.getBoundingClientRect()
      if (!bounds.width || !bounds.height) return
      if (now - lastDraw < interval) { schedule(); return }
      if (previousTime) elapsed += Math.min((now - previousTime) / 1000, 0.1)
      previousTime = now
      // Preserve the fractional frame remainder; avoid 30fps degenerating into20fps.
      lastDraw = now - ((now - lastDraw) % interval)
      const ratio = Math.min(window.devicePixelRatio || 1, lowPower ? 1 : 1.5)
      const width = Math.round(bounds.width * ratio)
      const height = Math.round(bounds.height * ratio)
      if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height }
      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      context.clearRect(0, 0, bounds.width, bounds.height)
      const cell = Math.min(bounds.width / ASCII_COLUMNS, bounds.height / (ASCII_ROWS * 2))
      const lineHeight = cell * 2
      const fontSize = cell / 0.6
      const left = (bounds.width - cell * ASCII_COLUMNS) / 2
      const top = (bounds.height - lineHeight * ASCII_ROWS) / 2
      context.font = `400 ${fontSize}px "IBM Plex Mono", monospace`
      context.fillStyle = color
      context.textBaseline = 'top'
      createAsciiFrame(elapsed).split('\n').forEach((line, row) => {
        for (let column = 0; column < line.length; column += 1) {
          if (line[column] !== ' ') context.fillText(line[column], left + column * cell, top + row * lineHeight)
        }
      })
      host.dataset.asciiPhase = elapsed.toFixed(3)
      host.dataset.asciiDraws = String(++draws)
      host.dataset.asciiReady = 'true'
      schedule()
    }
    const schedule = () => {
      if (!disposed && visible && !document.hidden && !frame) frame = requestAnimationFrame(draw)
    }
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting
      previousTime = 0
      if (!visible && frame) { cancelAnimationFrame(frame); frame = 0 }
      schedule()
    })
    observer.observe(host)
    const resize = new ResizeObserver(schedule)
    resize.observe(host)
    const theme = new MutationObserver(() => { color = getComputedStyle(host).color; schedule() })
    theme.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    window.addEventListener('resize', schedule)
    const visibility = () => {
      previousTime = 0
      if (document.hidden && frame) { cancelAnimationFrame(frame); frame = 0 }
      schedule()
    }
    document.addEventListener('visibilitychange', visibility)
    document.fonts?.ready.then(schedule)
    schedule()
    return () => {
      disposed = true
      cancelAnimationFrame(frame)
      observer.disconnect()
      resize.disconnect()
      theme.disconnect()
      window.removeEventListener('resize', schedule)
      document.removeEventListener('visibilitychange', visibility)
      delete host.dataset.asciiReady
    }
  }, [staticMode, mobile])

  return <div className="gl-ascii" ref={hostRef} aria-hidden="true" data-ascii-mode={staticMode ? 'static' : 'animated'}>
    <pre className="gl-ascii__fallback">{STATIC_ASCII_FRAME}</pre>
    {!staticMode && <canvas className="gl-ascii__canvas" ref={canvasRef} />}
  </div>
}
