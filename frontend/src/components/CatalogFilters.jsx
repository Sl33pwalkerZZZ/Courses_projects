import { Search, SlidersHorizontal, X } from 'lucide-react'
import './CatalogFilters.css'

export default function CatalogFilters({ search, onSearchChange, level, onLevelChange,
  direction, onDirectionChange, directions, hasFilters, onReset }) {
  return (
    <div className="catalog-filters" role="search" aria-label="Поиск и фильтры курсов">
      <div className="catalog-search">
        <label className="sr-only" htmlFor="course-search">Поиск по названию и описанию курса</label>
        <Search size={19} aria-hidden="true" />
        <input id="course-search" type="search" placeholder="Что вы хотите изучить?"
          value={search} onChange={(event) => onSearchChange(event.target.value)} />
      </div>
      <div className="catalog-select">
        <label htmlFor="course-direction">Направление</label>
        <select id="course-direction" value={direction} onChange={(event) => onDirectionChange(event.target.value)}>
          <option value="">Все направления</option>
          {directions.map((item) => <option key={item.slug} value={item.slug}>{item.name}</option>)}
        </select>
      </div>
      <div className="catalog-select">
        <label htmlFor="course-level">Сложность</label>
        <select id="course-level" value={level} onChange={(event) => onLevelChange(event.target.value)}>
          <option value="">Любой уровень</option>
          <option value="beginner">Начинающий</option>
          <option value="intermediate">Средний</option>
          <option value="advanced">Продвинутый</option>
        </select>
      </div>
      <button className="filter-reset" onClick={onReset} disabled={!hasFilters} aria-label="Сбросить поиск и фильтры">
        {hasFilters ? <X size={19} aria-hidden="true" /> : <SlidersHorizontal size={19} aria-hidden="true" />}
      </button>
    </div>
  )
}
