import { useEffect, useRef } from 'react'
import { createLiquidPixels, LIQUID_QUALITY } from '../../utils/liquidField'
import './LiquidEnvironment.css'

export default function LiquidEnvironment() {
  const hostRef = useRef(null)
  const canvasRef = useRef(null)
  useEffect(() => {
    const host = hostRef.current
    const canvas = canvasRef.current
    const context = canvas?.getContext('2d', { alpha: false })
    if (!host || !context) return
    const reduced = matchMedia('(prefers-reduced-motion: reduce)')
    const mobile = matchMedia('(max-width: 767px)')
    let frame = 0, disposed = false, last = 0, previous = 0, elapsed = 0, draws = 0
    let quality, image, dark, blendFrom = null, blendStart = 0
    let transitioning = false
    let reducedMode = reduced.matches
    const configure = () => {
      const old = image?.data.slice()
      quality = LIQUID_QUALITY[mobile.matches || navigator.hardwareConcurrency <= 4 ? 'mobile' : 'desktop']
      canvas.width = quality.width
      canvas.height = quality.height
      image = context.createImageData(quality.width, quality.height)
      const nextDark = document.documentElement.dataset.theme !== 'light'
      blendFrom = old && old.length === image.data.length && dark !== nextDark && document.documentElement.dataset.themeTransition === 'fallback' && !reducedMode ? old : null
      blendStart = performance.now()
      dark = document.documentElement.dataset.theme !== 'light'
      paint()
    }
    const paint = () => {
      createLiquidPixels(quality.width, quality.height, elapsed, dark, image.data)
      if (blendFrom) {
        const part = Math.min(1, (performance.now() - blendStart) / 420)
        const eased = 1 - (1 - part) ** 3
        for (let i = 0; i < image.data.length; i += 4) for (let channel = 0; channel < 3; channel++) {
          image.data[i + channel] = blendFrom[i + channel] * (1 - eased) + image.data[i + channel] * eased
        }
        if (part === 1) blendFrom = null
      }
      context.putImageData(image, 0, 0)
      host.dataset.liquidTime = elapsed.toFixed(3)
      host.dataset.liquidDraws = String(++draws)
      host.dataset.liquidMode = reducedMode ? 'static' : 'animated'
    }
    const schedule = () => {
      if (!disposed && !frame && !document.hidden && !reducedMode && (!transitioning || blendFrom)) frame = requestAnimationFrame(draw)
    }
    const draw = now => {
      frame = 0
      if (disposed || document.hidden || reducedMode || (transitioning && !blendFrom)) return
      const interval = 1000 / quality.fps
      if (now - last >= interval) {
        if (previous && !transitioning) elapsed += Math.min((now - previous) / 1000, .15)
        previous = now
        last = now - ((now - last) % interval)
        paint()
      }
      schedule()
    }
    const preferences = () => {
      reducedMode = matchMedia('(prefers-reduced-motion: reduce)').matches
      cancelAnimationFrame(frame); frame = 0; previous = 0
      configure(); schedule()
    }
    const visibility = () => {
      host.dataset.paused = String(document.hidden)
      previous = 0
      if (document.hidden) { cancelAnimationFrame(frame); frame = 0 }
      schedule()
    }
    const theme = new MutationObserver(records => {
      transitioning = !!document.documentElement.dataset.themeTransition
      host.dataset.themePaused = String(transitioning)
      if (records.some(record => record.attributeName === 'data-theme')) configure()
      cancelAnimationFrame(frame); frame = 0; previous = 0
      schedule()
    })
    theme.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'data-theme-transition'] })
    reduced.addEventListener('change', preferences)
    mobile.addEventListener('change', preferences)
    document.addEventListener('visibilitychange', visibility)
    configure(); visibility()
    return () => {
      disposed = true
      cancelAnimationFrame(frame)
      theme.disconnect()
      reduced.removeEventListener('change', preferences)
      mobile.removeEventListener('change', preferences)
      document.removeEventListener('visibilitychange', visibility)
    }
  }, [])
  return <div className="liquid-environment" ref={hostRef} aria-hidden="true"><canvas ref={canvasRef} /></div>
}
