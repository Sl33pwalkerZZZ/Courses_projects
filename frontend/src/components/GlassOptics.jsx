import { useEffect, useState } from 'react'
import { allowSvgOptics, createRefractionPixels } from '../utils/glassOptics'

// One static map shared only by small floating backplates; never filters UI text.
export default function GlassOptics() {
  const [map, setMap] = useState('')
  useEffect(() => {
    const mobile = matchMedia('(max-width: 767px)'), reduced = matchMedia('(prefers-reduced-motion: reduce)')
    let image = ''
    const update = () => {
      const enabled = allowSvgOptics({ userAgent: navigator.userAgent, cores: navigator.hardwareConcurrency || 4, mobile: mobile.matches, reduced: reduced.matches }) && CSS.supports('backdrop-filter', 'url("#ai-glass-refraction")')
      if (enabled && !image) {
        const canvas = document.createElement('canvas'); canvas.width = 128; canvas.height = 128
        const context = canvas.getContext('2d')
        if (context) {
          const pixels = context.createImageData(128, 128); pixels.data.set(createRefractionPixels())
          context.putImageData(pixels, 0, 0); image = canvas.toDataURL()
        }
      }
      setMap(image)
      document.documentElement.dataset.glassOptics = enabled && image ? 'svg' : 'frost'
    }
    update(); mobile.addEventListener('change', update); reduced.addEventListener('change', update)
    return () => { mobile.removeEventListener('change', update); reduced.removeEventListener('change', update); delete document.documentElement.dataset.glassOptics }
  }, [])
  return <svg className="glass-optics-defs" width="0" height="0" aria-hidden="true"><defs>
    <filter id="ai-glass-refraction" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
      <feImage href={map || undefined} x="0" y="0" width="100%" height="100%" preserveAspectRatio="none" result="edgeMap" />
      <feDisplacementMap in="SourceGraphic" in2="edgeMap" scale="14" xChannelSelector="R" yChannelSelector="G" />
    </filter>
  </defs></svg>
}
