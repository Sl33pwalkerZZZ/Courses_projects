import { useEffect, useRef } from 'react'
import { motion, useSpring, useTransform } from 'motion/react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../../theme/useTheme'
import { useMediaQuery, useSceneActivity } from './useSceneActivity'
import auraDark from '../../assets/amethyst/aura-dark.svg'
import headDark from '../../assets/amethyst/head-dark.svg'
import eyeDark from '../../assets/amethyst/eye-dark.svg'
import pupilDark from '../../assets/amethyst/pupil-dark.svg'
import particle1Dark from '../../assets/amethyst/particle-1-dark.svg'
import particle2Dark from '../../assets/amethyst/particle-2-dark.svg'
import particle3Dark from '../../assets/amethyst/particle-3-dark.svg'
import auraLight from '../../assets/amethyst/aura-light.svg'
import headLight from '../../assets/amethyst/head-light.svg'
import eyeLight from '../../assets/amethyst/eye-light.svg'
import pupilLight from '../../assets/amethyst/pupil-light.svg'
import particle1Light from '../../assets/amethyst/particle-1-light.svg'
import particle2Light from '../../assets/amethyst/particle-2-light.svg'
import particle3Light from '../../assets/amethyst/particle-3-light.svg'

const layers = {
  dark: [auraDark, headDark, eyeDark, pupilDark, particle1Dark, particle2Dark, particle3Dark],
  light: [auraLight, headLight, eyeLight, pupilLight, particle1Light, particle2Light, particle3Light],
}
const bound = (value) => Math.max(-1, Math.min(1, value))

export default function AICompanion() {
  const { t } = useTranslation()
  const theme = useTheme()?.theme || 'light'
  const [aura, head, eye, pupil, particle1, particle2, particle3] = layers[theme]
  const ref = useRef(null)
  const reduced = useReducedMotion()
  const active = useSceneActivity(ref, !reduced)
  const fine = useMediaQuery('(min-width: 901px) and (hover: hover) and (pointer: fine)')
  const eyeX = useSpring(-4, { stiffness: 230, damping: 22 })
  const eyeY = useSpring(-1, { stiffness: 230, damping: 22 })
  const rotate = useSpring(0, { stiffness: 100, damping: 16 })
  const headY = useSpring(0, { stiffness: 100, damping: 16 })
  const interest = useSpring(0, { stiffness: 180, damping: 20 })
  const blink = useSpring(1, { stiffness: 600, damping: 35 })
  const eyeScale = useTransform([blink, interest], ([open, curious]) => open * (1 + curious * .08))
  const headScale = useTransform(interest, [0, 1], [1, 1.025])

  useEffect(() => {
    const scene = ref.current?.closest('.signal-hero, .auth-intro')
    function rest(immediate = false) {
      const method = immediate ? 'jump' : 'set'
      eyeX[method](-4); eyeY[method](-1); rotate[method](0); headY[method](0); interest[method](0)
    }
    if (!scene || !active) { rest(true); blink.jump(1); return }
    let reopen
    const interval = setInterval(() => { blink.set(.12); reopen = setTimeout(() => blink.set(1), 140) }, 4600)
    function move(event) {
      const box = ref.current.getBoundingClientRect()
      const x = bound((event.clientX - box.left - box.width / 2) / 180)
      const y = bound((event.clientY - box.top - box.height / 2) / 180)
      eyeX.set(x * 7 - 4); eyeY.set(y * 7 - 1)
      rotate.set(x * 4); headY.set(y * 2)
      interest.set(event.target.closest('a, button') ? 1 : 0)
    }
    const leave = () => rest()
    if (fine) { scene.addEventListener('pointermove', move, { passive: true }); scene.addEventListener('pointerleave', leave) }
    return () => { clearInterval(interval); clearTimeout(reopen); scene.removeEventListener('pointermove', move); scene.removeEventListener('pointerleave', leave); rest(true); blink.jump(1) }
  }, [active, fine, eyeX, eyeY, rotate, headY, interest, blink])

  return <figure ref={ref} className="ai-companion" aria-hidden="true" data-motion-active={active} data-tracking={active && fine ? 'pointer' : 'ambient'}>
    <svg className="companion-scene" width="340" height="340" viewBox="0 0 340 340" focusable="false">
      <g className="companion-aura"><image href={aura} x="66" y="46" width="208" height="208" /></g>
      <g className="companion-drift">
        <motion.g className="companion-face" style={{ rotate, y: headY, scale: headScale, transformOrigin: '170px 151px' }}>
          <image href={head} x="95" y="76" width="151" height="151" />
          <motion.g className="companion-eyes" style={{ scaleY: eyeScale, transformOrigin: '170px 142px' }}>
            <image href={eye} x="127" y="124" width="36" height="36" />
            <image href={eye} x="188" y="124" width="36" height="36" />
            <motion.g className="companion-pupils" style={{ x: eyeX, y: eyeY }}>
              <image href={pupil} x="142" y="136" width="14" height="14" />
              <image href={pupil} x="203" y="136" width="14" height="14" />
            </motion.g>
          </motion.g>
        </motion.g>
      </g>
      <g className="companion-satellites"><image href={particle1} x="37" y="31" width="12" height="12" /><image href={particle2} x="287" y="214" width="8" height="8" /><image href={particle3} x="55" y="291" width="9" height="9" /></g>
    </svg>
    <figcaption>{t('amethyst.companion')}</figcaption>
  </figure>
}
