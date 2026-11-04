import { useId, useRef, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, Library, ClipboardCheck, FileUp, Users, ShieldCheck, UserCog, ChevronDown } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function StudioNavigation({ identity }) {
  const { t } = useTranslation()
  const { pathname } = useLocation()
  const [openPath, setOpenPath] = useState(null)
  const open = openPath === pathname
  const id = useId()
  const toggle = useRef(null)
  function close() {
    setOpenPath(null)
    if (toggle.current?.offsetParent !== null) toggle.current?.focus()
  }
  const links = [
    ['/instructor', 'dashboard', LayoutDashboard],
    ['/instructor/courses', identity.is_moderator ? 'allCourses' : 'courses', Library],
    ['/instructor/submissions', 'submissions', ClipboardCheck],
    ['/instructor/import', 'import', FileUp],
    ...(identity.is_moderator ? [['/instructor/enrollment-requests', 'enrollmentRequests.title', Users], ['/instructor/reviews', 'reviews', ShieldCheck]] : []),
    ...(identity.can_manage_instructors ? [['/instructor/instructors', 'instructors', UserCog]] : []),
  ]
  const current = links.find(([url]) => url === '/instructor' ? pathname === url : pathname.startsWith(url)) || links[0]
  return <div className="studio-command-bar" onKeyDown={event => { if (event.key === 'Escape' && open) { event.preventDefault(); close() } }}>
    <button ref={toggle} type="button" className="studio-navigation-toggle" aria-expanded={open} aria-controls={id}
      onClick={() => setOpenPath(open ? null : pathname)}><span>{t('studioVisual.navigation')}: {t(`instructorStudio.${current[1]}`)}</span><ChevronDown size={18} aria-hidden="true" /></button>
    <nav id={id} className="instructor-navigation studio-command-navigation" data-open={open} aria-label={t('instructorStudio.navigation')}>
      {links.map(([url, key, Icon]) => <NavLink key={url} to={url} end={url === '/instructor'} onClick={close}>
        <Icon size={18} strokeWidth={1.5} aria-hidden="true" /><span>{t(`instructorStudio.${key}`)}</span>
      </NavLink>)}
    </nav>
  </div>
}
