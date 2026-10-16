import { useEffect, useMemo, useRef } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'motion/react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import { useTranslation } from 'react-i18next'
import { graphemes, textWords } from '../../utils/motionText'
import { useMediaQuery, useSceneActivity } from './useSceneActivity'

function Letter({ children, index, centers, pointerX, pointerY, active }) {
  const proximity = useTransform([pointerX, pointerY], ([x, y]) => {
    const point = centers.current[index]
    return point ? Math.max(0, 1 - Math.hypot(x - point.x, y - point.y) / 90) : 0
  })
  const spring = useSpring(proximity, { stiffness: 320, damping: 24, mass: .6 })
  const y = useTransform(spring, [0, 1], [0, -8])
  const rotate = useTransform(spring, [0, 1], [0, index % 2 ? 7 : -7])
  const scale = useTransform(spring, [0, 1], [1, 1.06])
  useEffect(() => { if (!active) spring.jump(0) }, [active, spring])
  return <motion.span className="animated-letter" data-letter={index} style={{ y, rotate, scale }}>{children}</motion.span>
}

export default function AnimatedText({ text, className = '' }) {
  const { i18n } = useTranslation()
  const ref = useRef(null)
  const centers = useRef([])
  const pointerX = useMotionValue(-1000), pointerY = useMotionValue(-1000)
  const reduced = useReducedMotion()
  const fine = useMediaQuery('(min-width: 901px) and (hover: hover) and (pointer: fine)')
  const enabled = fine && !reduced
  const active = useSceneActivity(ref, enabled)
  const words = useMemo(() => textWords(text).map((word) => ({ word, letters: graphemes(word, i18n.resolvedLanguage) })), [text, i18n.resolvedLanguage])
  useEffect(() => {
    if (!active || !ref.current) { pointerX.set(-1000); pointerY.set(-1000); return }
    const host = ref.current
    function measure() {
      const box = host.getBoundingClientRect()
      centers.current = [...host.querySelectorAll('[data-letter]')].map((letter) => {
        const rect = letter.getBoundingClientRect()
        return { x: rect.left + rect.width / 2 - box.left, y: rect.top + rect.height / 2 - box.top }
      })
    }
    function move(event) {
      const box = host.getBoundingClientRect()
      pointerX.set(event.clientX - box.left); pointerY.set(event.clientY - box.top)
    }
    function leave() { pointerX.set(-1000); pointerY.set(-1000) }
    const observer = new ResizeObserver(measure)
    observer.observe(host); measure()
    host.addEventListener('pointerenter', measure)
    host.addEventListener('pointermove', move, { passive: true })
    host.addEventListener('pointerleave', leave)
    return () => { observer.disconnect(); host.removeEventListener('pointerenter', measure); host.removeEventListener('pointermove', move); host.removeEventListener('pointerleave', leave); leave() }
  }, [active, text, pointerX, pointerY])
  let index = 0
  return <span ref={ref} className={`animated-text ${className}`.trim()} data-animated-text={enabled ? 'active' : 'static'}>
    <span className="sr-only">{text}</span>
    <span aria-hidden="true">{!enabled ? text : words.map(({ word, letters }, wordIndex) => /^\s+$/u.test(word) ? word : <span className="animated-word" key={wordIndex}>
      {letters.map((letter) => <Letter key={index} index={index++} centers={centers} pointerX={pointerX} pointerY={pointerY} active={active}>{letter}</Letter>)}
    </span>)}</span>
  </span>
}
