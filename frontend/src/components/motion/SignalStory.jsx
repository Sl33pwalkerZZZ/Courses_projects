import { useRef } from 'react'
import { ArrowDown, BookOpen, Compass, KeyRound, Workflow } from 'lucide-react'
import { motion, useScroll, useSpring, useTransform } from 'motion/react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import { useTranslation } from 'react-i18next'
import { useMediaQuery } from './useSceneActivity'
import AnimatedText from './AnimatedText'

const stages = ['discover', 'connect', 'practice']
const icons = [Compass, KeyRound, Workflow]

function Chapter({ stage, index, progress }) {
  const { t } = useTranslation()
  const start = index / 3, end = (index + 1) / 3
  const opacity = useTransform(progress, [Math.max(0, start - .04), start + .025, end - .055, Math.min(1, end + .025)], [index ? 0 : 1, 1, 1, index === 2 ? 1 : 0])
  const y = useTransform(progress, [start, end], [12, -12])
  const scale = useTransform(progress, [start, end], [1, 1.025])
  return <motion.li className="signal-story-chapter" style={{ opacity, y, scale }}>
    <span className="story-index">0{index + 1} / {t(`amethyst.story.${stage}.label`)}</span>
    <h3>{t(`amethyst.story.${stage}.title`)}</h3><p>{t(`amethyst.story.${stage}.description`)}</p>
  </motion.li>
}

function StoryOrbit({ progress }) {
  const farY = useTransform(progress, [0, 1], [24, -24])
  const nearY = useTransform(progress, [0, 1], [40, -40])
  const rotation = useTransform(progress, [0, 1], [-20, 25])
  const path = useTransform(progress, [0, .85], [.08, 1])
  const coreScale = useTransform(progress, [0, .65, 1], [.9, 1.05, 1.12])
  return <div className="story-orbit" aria-hidden="true">
    <motion.svg viewBox="0 0 440 440" style={{ y: farY, rotate: rotation }}>
      <circle className="story-orbit-track" cx="220" cy="220" r="168" />
      <ellipse className="story-orbit-track" cx="220" cy="220" rx="168" ry="98" transform="rotate(-32 220 220)" />
      <motion.path className="story-connections" d="M90 138L322 102L346 304L150 344L90 138L346 304L322 102L150 344" style={{ pathLength: path }} />
      {[[90,138],[322,102],[346,304],[150,344]].map(([cx,cy]) => <circle className="story-node" key={cx} cx={cx} cy={cy} r="7" />)}
    </motion.svg>
    <motion.div className="story-core" style={{ scale: coreScale }}>AI<span aria-hidden="true">✦</span></motion.div>
    <motion.span className="story-fragment story-fragment-one" style={{ y: nearY }}><BookOpen size={22} /></motion.span>
    <motion.span className="story-fragment story-fragment-two" style={{ y: farY }}><Workflow size={22} /></motion.span>
  </div>
}

function AnimatedStory() {
  const { t } = useTranslation()
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end end'] })
  const progress = useSpring(scrollYProgress, { stiffness: 150, damping: 30, restDelta: .001 })
  const progressX = useTransform(progress, [0, 1], [0, 1])
  return <section ref={ref} id="signal-story" className="signal-story" aria-labelledby="signal-story-title">
    <div className="signal-story-sticky">
      <header className="story-topline"><div><p className="studio-eyebrow">{t('amethyst.story.eyebrow')}</p>
        <h2 id="signal-story-title"><AnimatedText text={t('amethyst.story.title')} /></h2></div>
        <a href="#course-library">{t('journey.skip')}<ArrowDown size={16} aria-hidden="true" /></a></header>
      <div className="story-composition">
        <ol className="story-chapters" aria-hidden="true">{stages.map((stage, index) => <Chapter key={stage} stage={stage} index={index} progress={progress} />)}</ol>
        <StoryOrbit progress={progress} />
      </div>
      <ol className="sr-only">{stages.map((stage) => <li key={stage}><h3>{t(`amethyst.story.${stage}.title`)}</h3><p>{t(`amethyst.story.${stage}.description`)}</p></li>)}</ol>
      <div className="story-pathway" aria-hidden="true"><motion.span style={{ scaleX: progressX }} />{stages.map((stage, index) => <span className="story-pathway-step" key={stage}>0{index + 1}<span>{t(`amethyst.story.${stage}.label`)}</span></span>)}</div>
      <p className="story-scroll-note">{t('amethyst.story.scroll')}</p>
    </div>
  </section>
}

function StaticStory() {
  const { t } = useTranslation()
  return <section id="signal-story" className="signal-story-static" aria-labelledby="signal-story-title">
    <p className="studio-eyebrow">{t('amethyst.story.eyebrow')}</p><h2 id="signal-story-title">{t('amethyst.story.title')}</h2>
    <ol>{stages.map((stage, index) => {
      const Icon = icons[index]
      return <li key={stage}><span className="story-static-icon" aria-hidden="true"><Icon size={22} /></span><div><span className="story-index">0{index + 1}</span><h3>{t(`amethyst.story.${stage}.title`)}</h3><p>{t(`amethyst.story.${stage}.description`)}</p></div></li>
    })}</ol>
    <a className="story-static-link" href="#course-library">{t('catalog.explore')}<ArrowDown size={16} aria-hidden="true" /></a>
  </section>
}

export default function SignalStory() {
  const reduced = useReducedMotion()
  const compact = useMediaQuery('(max-width: 900px), (max-height: 620px)')
  return reduced || compact ? <StaticStory /> : <AnimatedStory />
}
