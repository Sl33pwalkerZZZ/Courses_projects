import { useRef } from 'react'
import { ArrowDown, BookOpen, FileText, Network, Workflow } from 'lucide-react'
import { motion, useReducedMotion, useScroll, useTransform } from 'motion/react'
import { useTranslation } from 'react-i18next'
import './KnowledgeJourney.css'

const STAGES = [
  { key: 'ai', start: 0, end: 0.2 },
  { key: 'knowledge', start: 0.2, end: 0.4 },
  { key: 'automation', start: 0.4, end: 0.6 },
  { key: 'learning', start: 0.6, end: 0.78 },
  { key: 'catalog', start: 0.78, end: 1 },
]

// CSS reduces this distance on smaller screens without scroll-driven React state.
const parallaxOffset = (pixels) => `calc(${pixels}px * var(--journey-depth))`

function Chapter({ stage, index, progress }) {
  const { t } = useTranslation()
  const { start, end, key } = stage
  const enter = start === 0 ? 0 : start - 0.02
  const opacity = useTransform(progress, [enter, start + 0.02, end - 0.04, end], [start === 0 ? 1 : 0, 1, 1, 0])
  const y = useTransform(progress, [enter, start + 0.025, end], [18, 0, -12])
  const clipPath = useTransform(progress, [enter, start + 0.035], ['inset(35% 0 0 0)', 'inset(0% 0 0 0)'])

  return (
    <motion.li className="journey-chapter" style={{ opacity, y }}>
      <p className="eyebrow"><span className="journey-number">{String(index + 1).padStart(2, '0')}</span>{t(`journey.${key}.label`)}</p>
      <div className="journey-title-mask"><motion.h2 style={{ clipPath }}>{t(`journey.${key}.title`)}</motion.h2></div>
      <p className="journey-description">{t(`journey.${key}.description`)}</p>
    </motion.li>
  )
}

function Fragment({ name, Icon, index, progress }) {
  const { t } = useTranslation()
  const opacity = useTransform(progress, [0.16, 0.28, 0.73, 0.84], [0, 1, 1, 0])
  const y = useTransform(progress, [0.16, 0.4, 0.82], [36 + index * 5, 0, -12 - index * 4].map(parallaxOffset))
  const x = useTransform(progress, [0.2, 0.58, 0.82], [index % 2 ? 12 : -12, 0, index % 2 ? -8 : 8].map(parallaxOffset))

  return (
    <motion.div className={`journey-fragment journey-fragment-${index}`} style={{ opacity, x, y }}>
      <Icon size={18} strokeWidth={1.2} />
      <span>{t(`journey.fragments.${name}`)}</span>
      <i /><i />
    </motion.div>
  )
}

function StageMarker({ stage, progress }) {
  const scaleX = useTransform(progress, [stage.start, stage.end], [0, 1])
  return <span><motion.i style={{ scaleX }} /></span>
}

function AnimatedJourney() {
  const { t } = useTranslation()
  const section = useRef(null)
  const { scrollYProgress: progress } = useScroll({ target: section, offset: ['start start', 'end end'] })
  const farY = useTransform(progress, [0, 1], [24, -24].map(parallaxOffset))
  const middleY = useTransform(progress, [0, 1], [12, -18].map(parallaxOffset))
  const orbitRotation = useTransform(progress, [0, 0.8], [-12, 12])
  const sceneOpacity = useTransform(progress, [0, 0.79, 0.9], [1, 1, 0])
  const networkOpacity = useTransform(progress, [0.34, 0.46, 0.76, 0.86], [0, 0.75, 0.55, 0])
  const connections = useTransform(progress, [0.36, 0.6], [0, 1])
  const learningOpacity = useTransform(progress, [0.56, 0.64, 0.77, 0.84], [0, 1, 1, 0])
  const completion = useTransform(progress, [0.6, 0.76], [0, 1])
  // The filled core physically covers earlier layers, then shares the catalog's ink surface.
  const portalScale = useTransform(progress, [0, 0.73, 0.79, 0.84, 0.9, 1], [1, 1, 1.2, 3.5, 16, 32])
  const coreLabelOpacity = useTransform(progress, [0.78, 0.83], [1, 0])

  return (
    <section ref={section} className="knowledge-journey" aria-label={t('journey.label')}>
      <div className="journey-sticky">
        <div className="journey-scene">
          <motion.div className="journey-grid" style={{ y: farY, opacity: sceneOpacity }} aria-hidden="true" />
          <div className="journey-topline">
            <p className="eyebrow">{t('journey.eyebrow')}</p>
            <a href="#course-library" className="journey-skip">{t('journey.skip')}<ArrowDown size={15} aria-hidden="true" /></a>
          </div>
          <ol className="journey-chapters">
            {STAGES.map((stage, index) => <Chapter key={stage.key} stage={stage} index={index} progress={progress} />)}
          </ol>
          <div className="journey-visual" aria-hidden="true">
            <div className="journey-field">
              <motion.div className="journey-orbits" style={{ y: middleY, rotate: orbitRotation, opacity: sceneOpacity }}>
                <span /><span /><span />
              </motion.div>
              <motion.svg className="journey-network" viewBox="0 0 600 600" fill="none" style={{ opacity: networkOpacity, y: middleY }}>
                {['M300 300 L126 138 L460 142 L300 300', 'M300 300 L114 424 L468 432 L300 300', 'M126 138 L114 424', 'M460 142 L468 432'].map((d) => (
                  <motion.path key={d} d={d} style={{ pathLength: connections }} />
                ))}
                {[[126, 138], [460, 142], [114, 424], [468, 432]].map(([cx, cy]) => <circle key={cx} cx={cx} cy={cy} r="4" />)}
              </motion.svg>
              <Fragment name="knowledge" Icon={BookOpen} index={0} progress={progress} />
              <Fragment name="research" Icon={FileText} index={1} progress={progress} />
              <Fragment name="documents" Icon={Network} index={2} progress={progress} />
              <Fragment name="workflows" Icon={Workflow} index={3} progress={progress} />
              <motion.div className="journey-learning" style={{ opacity: learningOpacity }}>
                <svg viewBox="0 0 300 300" fill="none">
                  <circle className="journey-ring-track" cx="150" cy="150" r="132" />
                  <motion.circle className="journey-ring-progress" cx="150" cy="150" r="132" style={{ pathLength: completion }} />
                </svg>
                <span className="journey-learning-note">{t('journey.learning.note')}</span>
              </motion.div>
            </div>
            <div className="journey-core-anchor">
              <motion.div className="journey-portal" style={{ '--portal-scale': portalScale }}><span /></motion.div>
              <motion.span className="journey-core-label" style={{ opacity: coreLabelOpacity }}>{t('journey.core')}</motion.span>
            </div>
          </div>
          <motion.div className="journey-bottomline" style={{ opacity: sceneOpacity }}>
            <p>{t('journey.scrollHint')}</p>
            <div className="journey-markers" aria-hidden="true">{STAGES.map((stage) => <StageMarker key={stage.key} stage={stage} progress={progress} />)}</div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

function StaticJourney() {
  const { t } = useTranslation()
  return (
    <section className="knowledge-journey journey-static" aria-label={t('journey.label')}>
      <p className="eyebrow">{t('journey.eyebrow')}</p>
      <ol>
        {STAGES.map(({ key }, index) => <li key={key}>
          <span className="journey-number" aria-hidden="true">{String(index + 1).padStart(2, '0')}</span>
          <div><h2>{t(`journey.${key}.title`)}</h2><p>{t(`journey.${key}.description`)}</p></div>
        </li>)}
      </ol>
      <a href="#course-library" className="journey-skip">{t('journey.skip')}<ArrowDown size={15} aria-hidden="true" /></a>
    </section>
  )
}

export default function KnowledgeJourney() {
  const reducedMotion = useReducedMotion()
  return reducedMotion ? <StaticJourney /> : <AnimatedJourney />
}
