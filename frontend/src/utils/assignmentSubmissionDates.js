function formatTimestamp(value, locale) {
  if (typeof value !== 'string') return null
  const parts = value.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(Z|([+-])(\d{2}):(\d{2}))$/i)
  if (!parts) return null

  const [, yearText, monthText, dayText, hourText, minuteText, secondText, , , offsetHourText, offsetMinuteText] = parts
  const year = Number(yearText)
  const month = Number(monthText)
  const day = Number(dayText)
  const hour = Number(hourText)
  const minute = Number(minuteText)
  const second = Number(secondText)
  const offsetHour = Number(offsetHourText || 0)
  const offsetMinute = Number(offsetMinuteText || 0)
  const leapYear = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)
  const daysInMonth = [31, leapYear ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  if (month < 1 || month > 12 || day < 1 || day > daysInMonth[month - 1]
      || hour > 23 || minute > 59 || second > 59 || offsetHour > 23 || offsetMinute > 59) return null

  const date = new Date(value)
  if (!Number.isFinite(date.getTime())) return null

  try {
    return {
      dateTime: date.toISOString(),
      label: new Intl.DateTimeFormat(locale || 'en', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }).format(date),
    }
  } catch {
    return {
      dateTime: date.toISOString(),
      label: new Intl.DateTimeFormat('en', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }).format(date),
    }
  }
}

export function formatSubmissionTimestamps(submission, locale) {
  return {
    submittedAt: formatTimestamp(submission?.submitted_at, locale),
    reviewedAt: formatTimestamp(submission?.reviewed_at, locale),
  }
}
