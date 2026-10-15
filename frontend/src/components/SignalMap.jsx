import { motion, useReducedMotion } from 'motion/react'
import blueField from '../assets/signal-map/blue-field.svg'
import tealField from '../assets/signal-map/teal-field.svg'
import core from '../assets/signal-map/core.svg'
import './SignalMap.css'

// Original editable Figma layers stay local and keep their intrinsic geometry.
// Only the decorative signal trace animates once; the core is always visible.
export default function SignalMap() {
  const reducedMotion = useReducedMotion()
  return (
    <div className="signal-map" aria-hidden="true">
      <div className="signal-map-stage">
        <img className="signal-map-blue" src={blueField} alt="" width="340" height="340" />
        <img className="signal-map-teal" src={tealField} alt="" width="188" height="188" />
        <img className="signal-map-core" src={core} alt="" width="86" height="86" />
        <svg className="signal-map-trace" viewBox="0 0 340 340" fill="none" focusable="false">
          <motion.path d="M30 170 H94 L132 132 H208 L246 170 H310"
            initial={reducedMotion ? false : { pathLength: 0 }} animate={{ pathLength: 1 }}
            transition={{ duration: reducedMotion ? 0 : 0.48, ease: [0.2, 0.8, 0.2, 1] }} />
          <path d="M94 170 V218 H132 M246 170 V96 H208" className="signal-map-branch" />
          {[[30,170],[132,132],[208,132],[310,170],[132,218],[208,96]].map(([cx,cy]) => (
            <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="4" />
          ))}
        </svg>
      </div>
    </div>
  )
}
