// One controller per provider. No DOM cloning, route keys, or application snapshots.
export const REVEAL_DURATION = 720
export const FALLBACK_DURATION = 420
export const REVEAL_EASING = 'cubic-bezier(.16,1,.3,1)'

export function revealOrigin(rect, width, height) {
  return { x: Math.max(0, Math.min(width, rect ? rect.left + rect.width / 2 : width / 2)),
    y: Math.max(0, Math.min(height, rect ? rect.top + rect.height / 2 : height / 2)) }
}

export function liquidContour(x, y, radius, phase = 0) {
  return `polygon(${Array.from({ length: 48 }, (_, i) => {
    const angle = i / 48 * Math.PI * 2
    const edge = 1 + .065 * Math.sin(angle * 3 + phase) + .035 * Math.cos(angle * 5 - phase)
    return `${(x + Math.cos(angle) * radius * edge).toFixed(2)}px ${(y + Math.sin(angle) * radius * edge).toFixed(2)}px`
  }).join(',')})`
}

export function createThemeTransition(doc, win) {
  let generation = 0, active = null, disposed = false, latestApply = null
  const root = doc.documentElement
  const reduced = () => win.matchMedia('(prefers-reduced-motion: reduce)').matches
  function cancel() {
    generation++
    active?.transition?.skipTransition()
    active?.animation?.cancel()
    if (active?.timer) win.clearTimeout(active.timer)
    active?.ripple?.remove()
    active = null
    delete root.dataset.themeTransition
  }
  function change(apply, rect) {
    if (disposed) return
    cancel()
    latestApply = apply
    const id = generation
    const current = () => id === generation && !disposed
    const finish = () => { if (current()) { active?.ripple?.remove(); active = null; delete root.dataset.themeTransition } }
    if (reduced() || doc.hidden) { apply(); return }
    const { x, y } = revealOrigin(rect, win.innerWidth, win.innerHeight)
    const fallback = () => {
      if (!current()) return
      root.dataset.themeTransition = 'fallback'
      const ripple = doc.createElement('div')
      ripple.className = 'theme-liquid-ripple'
      ripple.setAttribute('aria-hidden', 'true')
      ripple.style.left = `${x}px`; ripple.style.top = `${y}px`
      doc.body.append(ripple)
      // Establish old computed colors before changing the theme, including first use.
      void root.offsetWidth
      apply()
      active = { ripple, timer: win.setTimeout(finish, FALLBACK_DURATION + 80) }
    }
    if (typeof doc.startViewTransition !== 'function' || !win.CSS?.supports('clip-path', 'polygon(0px 0px,1px 0px,0px 1px)')) { fallback(); return }
    root.dataset.themeTransition = 'reveal'
    let applied = false
    const update = () => { if (current()) { apply(); applied = true } }
    try {
      const transition = doc.startViewTransition(update)
      active = { transition }
      transition.updateCallbackDone.catch(() => { /* Ready/finished handle enhancement failures. */ })
      transition.ready.then(() => {
        if (!current()) return
        const radius = Math.hypot(Math.max(x, win.innerWidth - x), Math.max(y, win.innerHeight - y)) * 1.13
        const animation = root.animate([0, .16, .36, .62, 1].map((part, i) => ({
          clipPath: liquidContour(x, y, Math.max(1, radius * part), i * .48), offset: part,
        })), { duration: win.innerWidth < 768 ? 560 : REVEAL_DURATION, easing: REVEAL_EASING,
          pseudoElement: '::view-transition-new(root)', fill: 'both' })
        active.animation = animation
        animation.finished.catch(() => {})
      }).catch(() => {
        if (!current()) return
        // A rejected enhancement must never prevent the requested theme update.
        if (!applied) update()
      })
      transition.finished.catch(() => {}).finally(finish)
    } catch { fallback() }
  }
  const interrupt = () => {
    if (active && (doc.hidden || reduced())) { const apply = latestApply; cancel(); apply?.() }
  }
  const preference = win.matchMedia('(prefers-reduced-motion: reduce)')
  preference.addEventListener('change', interrupt)
  doc.addEventListener('visibilitychange', interrupt)
  return { change, cancel, dispose() { cancel(); disposed = true; preference.removeEventListener('change', interrupt); doc.removeEventListener('visibilitychange', interrupt) } }
}
