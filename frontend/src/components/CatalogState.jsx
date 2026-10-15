import { Library, SearchX, WifiOff } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Button from './ui/Button'
import Surface from './ui/Surface'

export function CatalogState({ kind, onAction }) {
  const { t } = useTranslation()
  const error = kind === 'error'
  const filtered = kind === 'filtered'
  const Icon = error ? WifiOff : filtered ? SearchX : Library
  const title = error ? 'studio.catalogErrorTitle' : filtered ? 'catalog.emptyTitle' : 'studio.catalogEmptyTitle'
  const description = error ? 'catalog.error' : filtered ? 'catalog.emptyDescription' : 'catalog.noCoursesDescription'
  return (
    <Surface className="catalog-state" role={error ? 'alert' : undefined}>
      <span className="studio-state-icon"><Icon size={24} strokeWidth={1.75} aria-hidden="true" /></span>
      <h3>{t(title)}</h3>
      <p>{t(description)}</p>
      {(error || filtered) && <Button onClick={onAction}>{t(error ? 'common.retry' : 'common.reset')}</Button>}
    </Surface>
  )
}

export function CatalogSkeleton() {
  return (
    <div className="academic-course-grid" aria-hidden="true">
      {[0, 1, 2].map((index) => <Surface key={index} className="course-skeleton">
        <div className="studio-skeleton-heading"><i /><span /></div>
        <span /><span /><span /><span />
      </Surface>)}
    </div>
  )
}
