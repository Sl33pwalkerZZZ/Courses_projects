import { useTranslation } from 'react-i18next'
import { motion } from 'motion/react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'

export default function ActivityPulse({ days }) {
  const { t, i18n } = useTranslation()
  const reduced = useReducedMotion()
  const recent = days.slice(-28)
  const maximum = Math.max(1, ...recent.map((day) => day.count))
  const total = recent.reduce((count, day) => count + day.count, 0)
  const points = recent.map((day, i) => `${8 + i * 10},${68 - day.count / maximum * 52}`).join(' ')
  const date = new Intl.DateTimeFormat(i18n.resolvedLanguage, { dateStyle: 'medium', timeZone: 'UTC' })
  const formatDate = (value) => date.format(new Date(`${value}T00:00:00Z`))
  const label = t('playground.recentActivity', { count: total })
  return <figure className="play-activity-pulse" aria-label={label}>
    <figcaption><span className="eyebrow">{t('playground.activityPulse')}</span><strong>{label}</strong></figcaption>
    <svg viewBox="0 0 286 80" role="img" aria-label={t('playground.activityPulse')}>
      <path className="pulse-baseline" d="M8 68H278" />
      <motion.polyline points={points} initial={reduced ? false : { pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: reduced ? 0 : .35 }} />
      {recent.filter((day) => day.count > 0).map((day) => <circle key={day.date} cx={8 + recent.indexOf(day) * 10} cy={68 - day.count / maximum * 52} r="3"><title>{formatDate(day.date)}: {new Intl.NumberFormat(i18n.resolvedLanguage).format(day.count)}</title></circle>)}
    </svg>
    <details><summary>{t('playground.activityData')}</summary><dl>{recent.map((day) => <div key={day.date}><dt><time dateTime={day.date}>{formatDate(day.date)}</time></dt><dd>{new Intl.NumberFormat(i18n.resolvedLanguage).format(day.count)}</dd></div>)}</dl></details>
  </figure>
}
