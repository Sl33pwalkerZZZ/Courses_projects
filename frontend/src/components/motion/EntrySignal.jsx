import { useEffect, useRef, useState } from 'react'
import { motion } from 'motion/react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import { useSceneActivity } from './useSceneActivity'

let enteredThisRuntime = false
function initialMode() {
  if (enteredThisRuntime) return 'return'
  try { return typeof window !== 'undefined' && sessionStorage.getItem('amethyst-entry-seen') ? 'return' : 'first' }
  catch { return 'first' }
}

// Decorative parallel entrance, never a loading gate, overlay, focus target or timer dependency.
export default function EntrySignal() {
  const reduced = useReducedMotion()
  const [mode, setMode] = useState(initialMode)
  const ref = useRef(null)
  const active = useSceneActivity(ref, !reduced && mode === 'first')
  useEffect(() => {
    enteredThisRuntime = true
    try { sessionStorage.setItem('amethyst-entry-seen', '1') } catch { /* Optional preference. */ }
    if (mode !== 'first' || !active) return
    const timer = setTimeout(() => setMode('ready'), 650)
    return () => clearTimeout(timer)
  }, [mode, active])
  if (reduced || mode === 'return') return null
  return <div ref={ref} className="entry-signal" data-entry={mode} aria-hidden="true">
    <span>AI / COURSES</span>{active && <svg width="144" height="24" viewBox="0 0 144 24" focusable="false">
      <motion.path d="M4 12L34 4L70 20L108 6L140 12" fill="none" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: .48, ease: 'easeOut' }} />
      {[4, 34, 70, 108, 140].map((x, i) => <motion.circle key={x} cx={x} cy={[12,4,20,6,12][i]} r="2" initial={{ y: i % 2 ? 8 : -8 }} animate={{ y: 0 }} transition={{ duration: .45, delay: i * .025 }} />)}
    </svg>}
  </div>
}
