import { useEffect, useRef } from 'react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import { useTheme } from '../../theme/useTheme'
import '../../styles/playground.css'

// Decorative only: capped density/DPR/30fps, no work outside the viewport or tab.
export default function ParticleField() {
  const ref = useRef(null)
  const reduced = useReducedMotion()
  const theme = useTheme()?.theme
  useEffect(() => {
    if (reduced || !ref.current) return
    const canvas = ref.current, context = canvas.getContext('2d')
    if (!context) return
    const host = canvas.parentElement
    const palette = getComputedStyle(host)
    const line = palette.getPropertyValue('--v2-particle-line').trim()
    const dot = palette.getPropertyValue('--v2-particle-dot').trim()
    let width = 1, height = 1, points = [], frame = 0, visible = false, last = 0
    const pointer = { x: -1000, y: -1000 }
    const fine = window.matchMedia('(hover:hover) and (pointer:fine)')
    function resize() {
      const box = host.getBoundingClientRect()
      width = box.width; height = box.height
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5)
      canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio)
      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      points = Array.from({ length: width < 640 ? 10 : 24 }, (_, i) => ({
        x: ((i * 73 + 17) % 101) / 101 * width, y: ((i * 41 + 29) % 97) / 97 * height, phase: i * 1.7,
      }))
    }
    function draw(time) {
      if (!visible || document.hidden) return
      frame = requestAnimationFrame(draw)
      if (time - last < 33) return
      last = time; context.clearRect(0, 0, width, height)
      const active = points.map((p) => {
        const distance = Math.hypot(pointer.x - p.x, pointer.y - p.y)
        const pull = distance < 180 ? (1 - distance / 180) * .08 : 0
        return { x: p.x + Math.sin(time / 2400 + p.phase) * 10 + (pointer.x - p.x) * pull,
          y: p.y + Math.cos(time / 2900 + p.phase) * 10 + (pointer.y - p.y) * pull }
      })
      context.strokeStyle = line; context.fillStyle = dot
      active.forEach((p, i) => {
        context.beginPath(); context.arc(p.x, p.y, 2, 0, Math.PI * 2); context.fill()
        active.slice(i + 1).forEach((q) => {
          if (Math.hypot(p.x - q.x, p.y - q.y) < 150) { context.beginPath(); context.moveTo(p.x, p.y); context.lineTo(q.x, q.y); context.stroke() }
        })
      })
    }
    function sync() { cancelAnimationFrame(frame); if (visible && !document.hidden) frame = requestAnimationFrame(draw) }
    function move(event) { if (fine.matches) { const box = host.getBoundingClientRect(); pointer.x = event.clientX - box.left; pointer.y = event.clientY - box.top } }
    function leave() { pointer.x = -1000; pointer.y = -1000 }
    const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; sync() })
    const size = new ResizeObserver(resize)
    resize(); observer.observe(host); size.observe(host)
    host.addEventListener('pointermove', move); host.addEventListener('pointerleave', leave)
    document.addEventListener('visibilitychange', sync)
    return () => { cancelAnimationFrame(frame); observer.disconnect(); size.disconnect(); host.removeEventListener('pointermove', move); host.removeEventListener('pointerleave', leave); document.removeEventListener('visibilitychange', sync) }
  }, [reduced, theme])
  return reduced ? <svg className="particle-field" aria-hidden="true" viewBox="0 0 900 500" preserveAspectRatio="none"><path d="M20 400 200 120 450 350 700 80 880 300" fill="none" stroke="currentColor" /></svg>
    : <canvas className="particle-field" ref={ref} aria-hidden="true" />
}
