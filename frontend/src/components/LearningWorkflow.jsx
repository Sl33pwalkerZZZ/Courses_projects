import { ArrowUpRight, Compass, KeyRound, Workflow } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Surface from './ui/Surface'

const STEPS = [
  { key: 'explore', Icon: Compass },
  { key: 'access', Icon: KeyRound },
  { key: 'practice', Icon: Workflow },
]

// A short, readable replacement for the retired scroll-pinned journey.
export default function LearningWorkflow() {
  const { t } = useTranslation()
  return (
    <section id="learning-workflow" className="studio-workflow" aria-labelledby="workflow-title">
      <div className="studio-section-heading">
        <p className="studio-eyebrow">{t('studio.workflowLabel')}</p>
        <h2 id="workflow-title">{t('studio.workflowTitle')}</h2>
      </div>
      <ol>
        {STEPS.map(({ key, Icon }, index) => <Surface as="li" key={key}>
          <div className="studio-step-top"><Icon size={24} strokeWidth={1.75} aria-hidden="true" /><span aria-hidden="true">0{index + 1}</span></div>
          <h3>{t(`studio.workflow.${key}.title`)}</h3>
          <p>{t(`studio.workflow.${key}.description`)}</p>
        </Surface>)}
      </ol>
      <a className="studio-workflow-link" href="#course-library">{t('catalog.explore')}<ArrowUpRight size={18} aria-hidden="true" /></a>
    </section>
  )
}
