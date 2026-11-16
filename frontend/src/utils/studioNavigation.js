const popGuards = new WeakMap()

// Register before BrowserRouter subscribes. On window-target POP events,
// registration order matters: a later listener can run after React unmounts us.
// The permanent listener does nothing unless a Studio lesson editor is active.
export function installStudioPopGuard(win) {
  if (!popGuards.has(win)) {
    const registry = { handler: null }
    win.addEventListener('popstate', event => registry.handler?.(event), true)
    popGuards.set(win, registry)
  }
  return popGuards.get(win)
}

// BrowserRouter has no data-router blocker. Guard its navigation methods and
// native POP before the router's bubble listener; cancelled POPs are restored
// without delivering either navigation to React. No tokens/drafts enter history.
export function guardStudioNavigation(navigator, win, confirmLeave) {
  const originals = {}
  let index = win.history.state?.idx
  let restoring = false
  for (const method of ['push', 'replace', 'go']) {
    if (typeof navigator[method] !== 'function') continue
    originals[method] = navigator[method]
    navigator[method] = function (...args) {
      // go() produces POP, which is checked exactly once by the listener below.
      if (method !== 'go' && !confirmLeave()) return
      const result = originals[method].apply(this, args)
      if (method !== 'go') index = win.history.state?.idx
      return result
    }
  }
  const pop = event => {
    if (restoring) {
      restoring = false
      index = win.history.state?.idx
      event.stopImmediatePropagation()
      return
    }
    const next = win.history.state?.idx
    if (typeof index === 'number' && typeof next === 'number' && index !== next && !confirmLeave()) {
      event.stopImmediatePropagation()
      restoring = true
      win.history.go(index - next)
      return
    }
    index = next
  }
  const registry = installStudioPopGuard(win)
  registry.handler = pop
  return () => {
    if (registry.handler === pop) registry.handler = null
    for (const [method, original] of Object.entries(originals)) navigator[method] = original
  }
}
