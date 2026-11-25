import { ArrowUpRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function LearningWorkflow() {
  const { t } = useTranslation()
  return <section id="learning-workflow" className="gl-workflow" aria-labelledby="workflow-title">
    <div className="gl-workflow-intro"><h2 id="workflow-title">{t('landing.workflowTitle')}</h2><p>{t('landing.workflowIntro')}</p><a href="#course-library">{t('catalog.explore')}<ArrowUpRight size={18} aria-hidden="true"/></a></div>
    <ol>{['explore','access','practice'].map((key,index)=><li key={key}><span className="gl-step-number" aria-hidden="true">{index+1}</span><div><h3>{t(`studio.workflow.${key}.title`)}</h3><p>{t(`studio.workflow.${key}.description`)}</p></div></li>)}</ol>
  </section>
}
