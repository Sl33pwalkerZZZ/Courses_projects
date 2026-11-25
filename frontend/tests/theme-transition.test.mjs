import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createThemeTransition, liquidContour, revealOrigin } from '../src/theme/themeTransition.js'

function deferred() { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no }); return { promise, resolve, reject } }
function fixture({ reduced = false, native = false } = {}) {
  const transitions = [], nodes = [], timers = new Map(), events = new Map(), animations = []
  const preference = { matches: reduced, addEventListener(_, f) { this.listener = f }, removeEventListener() {} }
  const root = { dataset: {}, offsetWidth: 100, animate(frames, options) { const done = deferred(); const animation = { frames, options, finished: done.promise, complete() { done.resolve() }, cancel() { done.reject(Error('cancelled')) } }; animations.push(animation); return animation } }
  const doc = { documentElement: root, hidden: false, addEventListener(n, f) { events.set(n, f) }, removeEventListener(n) { events.delete(n) }, createElement() { const node = { style: {}, setAttribute() {}, remove() { this.removed = true } }; nodes.push(node); return node }, body: { append() {} } }
  if (native) doc.startViewTransition = callback => {
    const ready = deferred(), done = deferred(), update = deferred()
    const transition = { ready: ready.promise, finished: done.promise, updateCallbackDone: update.promise, skipTransition() { this.skipped = true; ready.reject(Error('skipped')); done.resolve() }, update() { callback(); update.resolve() }, rejectReady() { ready.reject(Error('snapshot failed')) }, readyNow() { ready.resolve() }, finish() { done.resolve() } }
    transitions.push(transition); return transition
  }
  const win = { innerWidth: 1440, innerHeight: 900, CSS: { supports: () => true }, matchMedia: () => preference, setTimeout(f) { const id = timers.size + 1; timers.set(id, f); return id }, clearTimeout(id) { timers.delete(id) } }
  const controller = createThemeTransition(doc, win)
  return { controller, doc, root, transitions, animations, nodes, timers, preference, events }
}
const tick = () => new Promise(resolve => setImmediate(resolve))

test('reveal originates at the control centre for pointer and keyboard; clamps stale/offscreen coordinates', () => {
  assert.deepEqual(revealOrigin({ left: 100, top: 20, width: 44, height: 44 }, 1440, 900), { x: 122, y: 42 })
  assert.deepEqual(revealOrigin(null, 320, 800), { x: 160, y: 400 })
  assert.deepEqual(revealOrigin({ left: -90, top: 999, width: 40, height: 40 }, 320, 800), { x: 0, y: 800 })
  const contour = liquidContour(122, 42, 300)
  assert.equal(contour.split(',').length, 48)
  assert.doesNotMatch(contour, /NaN|Infinity/)
  assert.notEqual(contour, liquidContour(122, 42, 300, .48))
})
test('unsupported API interpolates existing DOM without a clone and cleans its decorative ripple', () => {
  const f = fixture(); let updates = 0
  f.controller.change(() => updates++)
  assert.equal(updates, 1); assert.equal(f.root.dataset.themeTransition, 'fallback')
  assert.equal(f.nodes.length, 1)
  for (const timer of f.timers.values()) timer()
  assert.equal(f.nodes[0].removed, true); assert.equal(f.root.dataset.themeTransition, undefined)
  f.controller.dispose()
})
test('reduced motion and hidden document apply immediately without snapshots or overlays', () => {
  for (const hidden of [false, true]) {
    const f = fixture({ reduced: !hidden, native: true }); f.doc.hidden = hidden; let updates = 0
    f.controller.change(() => updates++)
    assert.equal(updates, 1); assert.equal(f.transitions.length, 0); assert.equal(f.nodes.length, 0)
    f.controller.dispose()
  }
})
test('native reveal commits once and animates only the new snapshot; completion cleans scope', async () => {
  const f = fixture({ native: true }); let updates = 0
  f.controller.change(() => updates++, { left: 40, top: 20, width: 44, height: 44 })
  assert.equal(updates, 0); f.transitions[0].update(); f.transitions[0].readyNow(); await tick()
  assert.equal(updates, 1); assert.equal(f.animations.length, 1)
  assert.equal(f.animations[0].options.pseudoElement, '::view-transition-new(root)')
  f.transitions[0].finish(); await tick(); assert.equal(f.root.dataset.themeTransition, undefined)
  f.controller.dispose()
})
test('rapid requests ignore delayed old callbacks and old cleanup cannot erase a newer transition', async () => {
  const f = fixture({ native: true }), updates = []
  f.controller.change(() => updates.push('dark')); f.controller.change(() => updates.push('light'))
  assert.equal(f.transitions[0].skipped, true)
  f.transitions[0].update(); f.transitions[1].update(); await tick()
  assert.deepEqual(updates, ['light']); assert.equal(f.root.dataset.themeTransition, 'reveal')
  f.transitions[1].readyNow(); await tick(); f.transitions[1].finish(); await tick()
  assert.equal(f.root.dataset.themeTransition, undefined); f.controller.dispose()
})
test('native API failure still changes theme through the safe fallback', () => {
  const f = fixture({ native: true }); f.doc.startViewTransition = () => { throw Error('unavailable') }; let updates = 0
  f.controller.change(() => updates++); assert.equal(updates, 1); assert.equal(f.root.dataset.themeTransition, 'fallback'); f.controller.dispose()
})
test('preference/visibility interruption settles latest requested state, cleanup never writes after disposal', async () => {
  const f = fixture({ native: true }); let updates = 0
  f.controller.change(() => updates++); f.preference.matches = true; f.preference.listener(); await tick()
  assert.equal(updates, 1); assert.equal(f.root.dataset.themeTransition, undefined)
  f.controller.dispose(); f.controller.change(() => updates++); assert.equal(updates, 1)
  assert.equal(f.events.size, 0)
})
test('fallback replacement removes old ripple and timer without stale cleanup', () => {
  const f = fixture(); let updates = 0
  f.controller.change(() => updates++); f.controller.change(() => updates++)
  assert.equal(f.nodes[0].removed, true); assert.equal(f.nodes[1].removed, undefined)
  assert.equal(f.timers.size, 1); assert.equal(updates, 2); f.controller.dispose()
  assert.equal(f.nodes[1].removed, true)
})

test('runtime snapshot or pseudo-element animation failure activates fallback once', async () => {
  for (const failure of ['ready', 'animate']) {
    const f = fixture({ native: true }); let updates = 0
    if (failure === 'animate') f.root.animate = () => { throw Error('pseudo animation unavailable') }
    f.controller.change(() => updates++)
    f.transitions[0].update()
    if (failure === 'ready') f.transitions[0].rejectReady()
    else f.transitions[0].readyNow()
    await tick(); await tick()
    assert.equal(updates, 1); assert.equal(f.root.dataset.themeTransition, 'fallback')
    assert.equal(f.nodes.length, 1); f.controller.dispose()
  }
})

test('completed reveal explicitly releases filled snapshot effects', async () => {
 const f = fixture({ native: true }); f.controller.change(() => {})
 f.transitions[0].update(); f.transitions[0].readyNow(); await tick()
 f.animations[0].complete(); await tick(); await tick()
 assert.equal(f.transitions[0].skipped, true)
 assert.equal(f.root.dataset.themeTransition, undefined)
 f.controller.dispose()
})
