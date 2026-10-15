import { Search, SlidersHorizontal, X } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Button from './ui/Button'
import './CatalogFilters.css'

export default function CatalogFilters({ search, onSearchChange, level, onLevelChange,
  direction, onDirectionChange, directions, hasFilters, onReset }) {
  const { t } = useTranslation()
  return (
    <div className="catalog-filters" role="search" aria-label={t('filters.label')}>
      <div className="catalog-search-group">
        <label htmlFor="course-search">{t('studio.searchLabel')}</label>
        <div className="catalog-search">
          <Search size={20} strokeWidth={1.75} aria-hidden="true" />
          <input id="course-search" type="search" placeholder={t('filters.placeholder')}
            value={search} onChange={(event) => onSearchChange(event.target.value)} />
        </div>
      </div>
      <div className="catalog-select">
        <label htmlFor="course-direction">{t('filters.direction')}</label>
        <select id="course-direction" value={direction} onChange={(event) => onDirectionChange(event.target.value)}>
          <option value="">{t('filters.allDirections')}</option>
          {directions.map((item) => <option key={item.slug} value={item.slug}>{item.name}</option>)}
        </select>
      </div>
      <div className="catalog-select">
        <label htmlFor="course-level">{t('filters.level')}</label>
        <select id="course-level" value={level} onChange={(event) => onLevelChange(event.target.value)}>
          <option value="">{t('filters.allLevels')}</option>
          <option value="beginner">{t('levels.beginner')}</option>
          <option value="intermediate">{t('levels.intermediate')}</option>
          <option value="advanced">{t('levels.advanced')}</option>
        </select>
      </div>
      <Button variant="secondary" className="filter-reset v2-icon-button" onClick={onReset} disabled={!hasFilters} aria-label={t('filters.reset')}>
        {hasFilters ? <X size={19} aria-hidden="true" /> : <SlidersHorizontal size={19} aria-hidden="true" />}
        <span className="filter-reset-label">{t('common.reset')}</span>
      </Button>
    </div>
  )
}
