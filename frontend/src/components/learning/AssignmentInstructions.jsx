import { useTranslation } from 'react-i18next'
import { rubricCriteria } from '../../utils/instructorStudio'
import './assignmentInstructions.css'

// Shared by the real student form and Studio's instructions-only preview.
// description is the sole persisted title/instructions field; never split or rewrite it.
export function AssignmentRubric() {
  const { t } = useTranslation()
  return <section aria-label={t('instructorStudio.assignmentReview.rubricTitle')}>
    <h4>{t('instructorStudio.assignmentReview.rubricTitle')}</h4>
    <dl className="assignment-instructions-rubric">{rubricCriteria.map(key => <div key={key}>
      <dt>{t(`instructorStudio.assignmentReview.rubric.${key}`)}</dt>
      <dd>{t('instructorStudio.assignmentAuthoring.scoreRange')}</dd>
    </div>)}</dl>
  </section>
}

export default function AssignmentInstructions({ assignment }) {
  return <div className="assignment-instructions">
    <p className="assignment-instructions-text">{assignment.description}</p>
    {assignment.learning_activity === 'final_media_project' && <AssignmentRubric />}
  </div>
}
