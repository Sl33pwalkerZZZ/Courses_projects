import { motion } from 'motion/react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import { useTranslation } from 'react-i18next'

export default function DiscoveryDirections({ directions, selected, onSelect }) {
  const { t } = useTranslation()
  const reduced = useReducedMotion()
  if (!directions.length) return null
  return <nav className="discovery-directions" aria-label={t('filters.direction')}>
    <button type="button" aria-pressed={!selected} onClick={() => onSelect('')}>{t('filters.allDirections')}</button>
    {directions.map((direction, index) => <motion.button key={direction.slug} type="button" aria-pressed={selected === direction.slug}
      initial={reduced ? false : { y: 8 }} whileInView={{ y: 0 }} viewport={{ once: true }}
      transition={{ duration: reduced ? 0 : .24, delay: reduced ? 0 : Math.min(index, 5) * .035 }} onClick={() => onSelect(direction.slug)}>
      <span aria-hidden="true">{String(index + 1).padStart(2, '0')}</span>{direction.name}
    </motion.button>)}
  </nav>
}
