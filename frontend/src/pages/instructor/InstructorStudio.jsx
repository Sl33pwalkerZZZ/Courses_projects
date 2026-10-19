import { Navigate, NavLink, Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import useAuth from '../../hooks/useAuth'
import useInstructor from '../../hooks/useInstructor'
import Button from '../../components/ui/Button'
import './instructor.css'

export default function InstructorStudio() {
  const { t } = useTranslation()
  const authed = useAuth()
  const { identity, loading, error, retry } = useInstructor()
  if (!authed) return <Navigate to="/login" replace />
  if (loading) return <p role="status">{t('common.loading')}</p>
  if (!identity) return <section className="instructor-studio"><h1>{t('instructorStudio.title')}</h1><p role="alert">{t(error ? 'instructorStudio.loadError' : 'instructorStudio.forbidden')}</p>{error && <Button onClick={retry}>{t('common.retry')}</Button>}</section>
  return <section className="instructor-studio" aria-labelledby="instructor-title">
    <header className="instructor-heading"><div><p className="eyebrow">AI COURSES / STUDIO</p><h1 id="instructor-title">{t('instructorStudio.title')}</h1><p>{t('instructorStudio.intro')}</p></div></header>
    <nav className="instructor-navigation" aria-label={t('instructorStudio.navigation')}>
      <NavLink to="/instructor" end>{t('instructorStudio.dashboard')}</NavLink>
      <NavLink to="/instructor/courses">{t('instructorStudio.courses')}</NavLink>
      <NavLink to="/instructor/import">{t('instructorStudio.import')}</NavLink>
      {identity.is_moderator && <><NavLink to="/instructor/reviews">{t('instructorStudio.reviews')}</NavLink><NavLink to="/instructor/instructors">{t('instructorStudio.instructors')}</NavLink></>}
    </nav>
    <Outlet context={{ identity }} />
  </section>
}
