import { useEffect, useMemo, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { buildActivityGrid } from '../utils/activity'
import './LearningActivityCalendar.css'

export default function LearningActivityCalendar({ activity }) {
  const { t, i18n } = useTranslation()
  const grid = useMemo(() => buildActivityGrid(activity, i18n.resolvedLanguage), [activity, i18n.resolvedLanguage])
  const [selectedDate, setSelectedDate] = useState(activity.end_date)
  const [focusedDay, setFocusedDay] = useState(null)
  const [hoveredDay, setHoveredDay] = useState(null)
  const buttons = useRef(new Map())
  const scrollRef = useRef(null)
  const dateFormat = new Intl.DateTimeFormat(i18n.resolvedLanguage, { dateStyle: 'long', timeZone: 'UTC' })
  const weekdayFormat = new Intl.DateTimeFormat(i18n.resolvedLanguage, { weekday: 'short', timeZone: 'UTC' })
  const detail = hoveredDay || focusedDay
  const label = (day) => t('activity.dayDetails', { count: day.count, date: dateFormat.format(new Date(`${day.date}T00:00:00Z`)) })

  useEffect(() => {
    // Show recent dates first when the calendar needs its own horizontal scroll.
    const scroll = scrollRef.current
    if (scroll) scroll.scrollLeft = scroll.scrollWidth
  }, [activity.end_date])

  function navigateDay(event, date) {
    const days = grid.weeks.flat().filter(Boolean)
    const index = days.findIndex((day) => day.date === date)
    const moves = { ArrowUp: -1, ArrowDown: 1, ArrowLeft: -7, ArrowRight: 7 }
    let nextIndex
    if (event.key in moves) nextIndex = Math.max(0, Math.min(days.length - 1, index + moves[event.key]))
    else if (event.key === 'Home') nextIndex = 0
    else if (event.key === 'End') nextIndex = days.length - 1
    else return
    event.preventDefault()
    const button = buttons.current.get(days[nextIndex].date)
    button?.focus({ preventScroll: true })
    button?.scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' })
  }

  return <div className="learning-activity-calendar">
    <div className="activity-calendar-scroll" ref={scrollRef} role="group" aria-label={t('activity.calendarLabel')}>
      <div className="activity-calendar-layout" style={{ '--activity-weeks': grid.weeks.length }}>
        <div className="activity-weekday-labels" aria-hidden="true">
          {[0, 2, 4].map((row) => <span key={row} style={{ gridRow: row + 2 }}>
            {weekdayFormat.format(new Date(Date.UTC(2024, 0, 1 + row)))}
          </span>)}
        </div>
        <div className="activity-calendar-grid">
          <div className="activity-month-labels" aria-hidden="true">
            {grid.months.map((month) => <span key={month.column} style={{ gridColumn: `${month.column + 1} / span ${Math.min(3, grid.weeks.length - month.column)}` }}>{month.label}</span>)}
          </div>
          <div className="activity-weeks">
            {grid.weeks.map((week, index) => <div className="activity-week" key={index}>
              {week.map((day, row) => day ? <button type="button" className="activity-day" data-level={day.level}
                data-date={day.date} key={day.date} aria-label={label(day)} title={label(day)}
                tabIndex={selectedDate === day.date ? 0 : -1}
                ref={(button) => { if (button) buttons.current.set(day.date, button); else buttons.current.delete(day.date) }}
                onFocus={() => { setSelectedDate(day.date); setFocusedDay(day); setHoveredDay(null) }} onBlur={() => setFocusedDay(null)}
                onMouseEnter={() => setHoveredDay(day)} onMouseLeave={() => setHoveredDay(null)}
                onClick={() => { setSelectedDate(day.date); setFocusedDay(day) }}
                onKeyDown={(event) => navigateDay(event, day.date)} />
                : <span className="activity-day-padding" key={`padding-${row}`} aria-hidden="true" />)}
            </div>)}
          </div>
        </div>
      </div>
    </div>
    <div className="activity-calendar-footer">
      <p className="activity-day-details" role="status" aria-live="polite">{detail ? label(detail) : t('activity.keyboardHelp')}</p>
      <div className="activity-legend" role="group" aria-label={t('activity.legendLabel')}>
        <span>{t('activity.less')}</span>
        {[0, 1, 2, 3, 4].map((level) => <span className="activity-legend-entry" key={level}>
          <span className="activity-legend-cell" data-level={level} aria-hidden="true" />
          <span>{t(`activity.intensity.${level}`)}</span>
        </span>)}
        <span>{t('activity.more')}</span>
      </div>
    </div>
    <p className="activity-calendar-note">{t('activity.timezoneNote', { timezone: activity.timezone })} <span>{t('activity.scrollHint')}</span></p>
  </div>
}
