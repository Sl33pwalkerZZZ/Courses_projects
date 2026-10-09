import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { CalendarDays } from 'lucide-react'
import api from '../api'
import { loadLearningActivity } from '../utils/activity'
import LearningActivityCalendar from './LearningActivityCalendar'

export function LearningActivityPanel({ activity, loading, error, onRetry }) {
  const { t, i18n } = useTranslation()
  const number = new Intl.NumberFormat(i18n.resolvedLanguage)
  return <section className="profile-learning-activity" aria-labelledby="profile-activity-title" aria-busy={loading}>
    <div className="profile-activity-heading"><div>
      <p className="eyebrow">{t('activity.eyebrow')}</p>
      <h2 id="profile-activity-title">{t('activity.title')}</h2>
      <p>{t('activity.description')}</p>
    </div><CalendarDays size={25} strokeWidth={1.4} aria-hidden="true" /></div>
    {error ? <div className="activity-load-error" role="alert">
      <p>{t('activity.loadError')}</p><button className="academic-button" type="button" onClick={onRetry}>{t('common.retry')}</button>
    </div> : loading || !activity ? <p className="activity-loading" role="status">{t('common.loading')}</p> : <>
      <dl className="activity-statistics">
        <div><dt>{t('activity.lessonsCompleted')}</dt><dd><strong>{number.format(activity.total_completed_lessons)}</strong><span>{t('activity.allTime')}</span></dd></div>
        <div><dt>{t('activity.activeDays')}</dt><dd><strong>{number.format(activity.active_days_last_365)}</strong><span>{t('activity.last365Days')}</span></dd></div>
        <div><dt>{t('activity.currentStreak')}</dt><dd><strong>{number.format(activity.current_streak_days)}</strong><span>{t('activity.streakUnit', { count: activity.current_streak_days })}</span></dd></div>
      </dl>
      <div className="profile-activity-calendar-card">
        {!activity.active_days_last_365 && <div className="activity-empty-message">
          <h3>{t(activity.total_completed_lessons ? 'activity.noRecentActivity' : 'activity.noActivity')}</h3><p>{t('activity.emptyDescription')}</p>
        </div>}
        <LearningActivityCalendar key={activity.end_date} activity={activity} />
      </div>
      <p className="activity-streak-note">{t('activity.streakNote')}</p>
    </>}
  </section>
}

export default function ProfileLearningActivity() {
  const [activity, setActivity] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    let active = true
    loadLearningActivity(api).then((data) => { if (active) setActivity(data) })
      .catch(() => { if (active) setError(true) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [retry])

  function retryLoading() {
    setLoading(true)
    setError(false)
    setRetry((value) => value + 1)
  }

  return <LearningActivityPanel activity={activity} loading={loading} error={error} onRetry={retryLoading} />
}
