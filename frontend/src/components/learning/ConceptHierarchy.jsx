import { useTranslation } from 'react-i18next'
import './concept-hierarchy.css'

export default function ConceptHierarchy({ items }) {
  const { t } = useTranslation()
  const relations = ['hierarchyAI', 'hierarchyML', 'hierarchyDL', 'hierarchyLLM']
  function level(index) {
    const item = items[index]
    return <ul className="concept-hierarchy-level"><li>
      <div className="concept-hierarchy-copy">
        <h4>{item.title}</h4>
        <p>{t(`learning.${relations[index]}`)}</p>
      </div>
      {index < items.length - 1 && level(index + 1)}
    </li></ul>
  }
  return <div className="concept-hierarchy">
    {level(0)}
    <p className="concept-hierarchy-boundary">{t('learning.hierarchyBoundary')}</p>
  </div>
}
