import { Navigate, Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import useAuth from '../../hooks/useAuth'
import useInstructor from '../../hooks/useInstructor'
import Button from '../../components/ui/Button'
import { canEnterStudio } from '../../utils/instructorIdentity'
import StudioNavigation from '../../components/instructor/StudioNavigation'
import './instructor.css'
import './studio-command.css'

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
  return <section className="instructor-studio studio-command-shell" aria-labelledby="instructor-title">
    <header className="instructor-heading"><div><p className="eyebrow">AI Courses / Studio</p><h1 id="instructor-title">{t('instructorStudio.title')}</h1><p>{t('instructorStudio.intro')}</p><p className="instructor-badge">{t('instructorStudio.effectiveRole')}: {t(`instructorStudio.roles.${identity.effective_role}`)}{identity.authority_source === 'superuser' && ` · ${t('instructorStudio.superuserOverride')}`}</p></div></header>
    <StudioNavigation identity={identity} />
    <Outlet context={{ identity }} />
  </section>
}
