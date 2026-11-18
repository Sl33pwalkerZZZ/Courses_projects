import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function QuizPreviewNotice({ courseId }) {
  const { t } = useTranslation()
  return <p>{t('instructorPreview.quiz')} {courseId && <Link to={`/instructor/courses/${courseId}/assessment`}>{t('instructorPreview.editQuiz')}</Link>}</p>
}
