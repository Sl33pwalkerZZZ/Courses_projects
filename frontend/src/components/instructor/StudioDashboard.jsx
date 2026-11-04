import { motion } from 'motion/react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, Plus, FileUp, Library, ClipboardCheck } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import Button from '../ui/Button'
import StudioCourseCollection from './StudioCourseCollection'
import { studioList } from '../../utils/instructorStudio'

export function StudioDataState({ resource, children }) {
  const { t } = useTranslation()
  if (resource.loading) return <div className="studio-resource-state" aria-busy="true"><p role="status">{t('common.loading')}</p><div className="studio-resource-skeleton" aria-hidden="true"><i /><i /><i /></div></div>
  if (resource.error) return <div className="studio-resource-state" role="alert"><h3>{t('instructorStudio.loadError')}</h3><p>{resource.error}</p><Button onClick={resource.reload} variant="secondary">{t('common.retry')}</Button></div>
  return children(resource.data)
}

export function StudioEntrance({ children }) {
  const reduced = useReducedMotion()
  return <motion.div className="studio-view" initial={reduced ? false : { y: 12 }} animate={{ y: 0 }} transition={{ duration: reduced ? 0 : .45, ease: [.2,.8,.2,1] }}>{children}</motion.div>
}

export function StudioPageHeading({ title, description }) {
  const { t } = useTranslation()
  return <header className="studio-page-heading"><div><p className="studio-overline">{t('studioVisual.workspace')}</p><h2>{title}</h2><p>{description}</p></div>
    <div className="studio-action-group"><Button to="/instructor/courses/new"><Plus size={18} aria-hidden="true" />{t('instructorStudio.newCourse')}</Button>
      <Button to="/instructor/import" variant="secondary"><FileUp size={18} aria-hidden="true" />{t('instructorStudio.import')}</Button></div></header>
}

export default function StudioDashboard({ metrics, projects, moderator = false }) {
  const { t, i18n } = useTranslation()
  const keys = ['courses','published','drafts','pending_publications','pending_submissions']
  return <StudioEntrance><StudioPageHeading title={t('instructorStudio.dashboard')} description={t('studioVisual.dashboardDescription')} />
    <StudioDataState resource={metrics}>{data => {
      const counts = data?.counts || data || {}
      return <dl className="studio-metric-strip">{keys.filter(key => Number.isFinite(counts[key])).map(key => <div key={key}>
        <dt>{t(`instructorStudio.metrics.${key}`)}</dt><dd>{new Intl.NumberFormat(i18n.resolvedLanguage).format(counts[key])}</dd></div>)}</dl>
    }}</StudioDataState>
    <div className="studio-workbench-heading"><div><p className="studio-overline">{t('studioVisual.continueWork')}</p><h3>{t(moderator ? 'instructorStudio.allCourses' : 'instructorStudio.courses')}</h3></div>
      <Link to="/instructor/courses">{t('studioVisual.viewAll')}<ArrowUpRight size={18} aria-hidden="true" /></Link></div>
    <StudioDataState resource={projects}>{data => <StudioCourseCollection courses={studioList(data).slice(0,4)} compact />}</StudioDataState>
    <section className="studio-shortcuts" aria-label={t('studioVisual.quickActions')}>
      <Link to="/instructor/submissions"><ClipboardCheck size={22} strokeWidth={1.5} aria-hidden="true" /><span><strong>{t('instructorStudio.submissions')}</strong><small>{t('studioVisual.reviewDescription')}</small></span><ArrowUpRight size={18} aria-hidden="true" /></Link>
      <Link to="/instructor/courses"><Library size={22} strokeWidth={1.5} aria-hidden="true" /><span><strong>{t('instructorStudio.courses')}</strong><small>{t('studioVisual.libraryDescription')}</small></span><ArrowUpRight size={18} aria-hidden="true" /></Link>
    </section>
  </StudioEntrance>
}
