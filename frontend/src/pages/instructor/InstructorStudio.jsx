import { Navigate, NavLink, Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import useAuth from '../../hooks/useAuth'
import useInstructor from '../../hooks/useInstructor'
import Button from '../../components/ui/Button'
import { canEnterStudio } from '../../utils/instructorIdentity'
import './instructor.css'

export function StudioAccessGuard({ children, moderator = false }) {
  const { t } = useTranslation()
  const authed = useAuth()
  const { identity, loading, error, retry } = useInstructor()
  if (!authed) return <Navigate to="/login" replace />
  if (loading) return <p role="status">{t('common.loading')}</p>
  if (error) return <section className="instructor-studio"><h1>{t('instructorStudio.title')}</h1><p role="alert">{t('instructorStudio.loadError')}</p><Button onClick={retry}>{t('common.retry')}</Button></section>
  if (!canEnterStudio(identity) || (moderator && !identity.is_moderator)) return <section className="instructor-studio" aria-labelledby="studio-forbidden-title"><h1 id="studio-forbidden-title">403 — {t('instructorStudio.accessDenied')}</h1><p role="alert">{t('instructorStudio.forbidden')}</p><Button to="/">{t('instructorStudio.returnToCourses')}</Button></section>
  // Capability changes also discard private state without changing JWT sessions.
  return <div key={`${identity.id}:${identity.effective_role}:${identity.authority_source}`}>{children || <Outlet context={{ identity }} />}</div>
}
export default function InstructorStudio() {
  return <StudioAccessGuard><StudioLayout /></StudioAccessGuard>
}
function StudioLayout() {
  const { t } = useTranslation()
  const { identity } = useInstructor()
  return <section className="instructor-studio" aria-labelledby="instructor-title">
    <header className="instructor-heading"><div><p className="eyebrow">AI COURSES / STUDIO</p><h1 id="instructor-title">{t('instructorStudio.title')}</h1><p>{t('instructorStudio.intro')}</p><p className="instructor-badge">{t('instructorStudio.effectiveRole')}: {t(`instructorStudio.roles.${identity.effective_role}`)}{identity.authority_source === 'superuser' && ` · ${t('instructorStudio.superuserOverride')}`}</p></div></header>
    <nav className="instructor-navigation" aria-label={t('instructorStudio.navigation')}>
      <NavLink to="/instructor" end>{t('instructorStudio.dashboard')}</NavLink>
      <NavLink to="/instructor/courses">{t(identity.is_moderator ? 'instructorStudio.allCourses' : 'instructorStudio.courses')}</NavLink>
      <NavLink to="/instructor/submissions">{t('instructorStudio.submissions')}</NavLink>
      <NavLink to="/instructor/import">{t('instructorStudio.import')}</NavLink>
      {identity.is_moderator && <NavLink to="/instructor/enrollment-requests">{t('instructorStudio.enrollmentRequests.title')}</NavLink>}
      {identity.is_moderator && <NavLink to="/instructor/reviews">{t('instructorStudio.reviews')}</NavLink>}
      {identity.can_manage_instructors && <NavLink to="/instructor/instructors">{t('instructorStudio.instructors')}</NavLink>}
    </nav>
    <Outlet context={{ identity }} />
  </section>
}
