const DAY = 24 * 60 * 60 * 1000

function dateValue(date) {
  if (typeof date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error('Invalid activity date')
  const value = Date.parse(`${date}T00:00:00Z`)
  if (!Number.isFinite(value) || new Date(value).toISOString().slice(0, 10) !== date) throw new Error('Invalid activity date')
  return value
}

function validCount(value) {
  return Number.isSafeInteger(value) && value >= 0
}

export function normalizeActivity(data, now = new Date()) {
  if (!data || typeof data !== 'object' || !Array.isArray(data.daily_counts)) throw new Error('Invalid activity response')
  // Compare calendar dates in the API's timezone, not the browser's local timezone.
  const parts = new Intl.DateTimeFormat('en', {
    timeZone: data.timezone, year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(now)
  if (typeof data.timezone !== 'string' || !data.timezone) throw new Error('Missing activity timezone')
  const part = (type) => parts.find((item) => item.type === type).value
  const today = `${part('year')}-${part('month')}-${part('day')}`
  const start = dateValue(data.start_date)
  const end = dateValue(data.end_date)
  if (end - start !== 364 * DAY || end > dateValue(today)) throw new Error('Invalid activity window')
  for (const name of ['total_completed_lessons', 'active_days_last_365', 'current_streak_days']) {
    if (!validCount(data[name])) throw new Error('Invalid activity statistic')
  }
  const counts = new Map()
  for (const day of data.daily_counts) {
    const value = dateValue(day?.date)
    if (!validCount(day.count) || value < start || value > end || counts.has(day.date)) throw new Error('Invalid daily activity')
    counts.set(day.date, day.count)
  }
  const dailyCounts = Array.from({ length: 365 }, (_, index) => {
    const date = new Date(start + index * DAY).toISOString().slice(0, 10)
    return { date, count: counts.get(date) || 0 }
  })
  const activeDays = dailyCounts.filter((day) => day.count > 0).length
  const totalInWindow = dailyCounts.reduce((sum, day) => sum + day.count, 0)
  if (activeDays !== data.active_days_last_365 || totalInWindow > data.total_completed_lessons
    || data.current_streak_days > data.total_completed_lessons || (!activeDays && data.current_streak_days)) {
    throw new Error('Inconsistent activity statistics')
  }
  return { ...data, daily_counts: dailyCounts }
}

export async function loadLearningActivity(client) {
  const { data } = await client.get('/my/activity/')
  return normalizeActivity(data)
}

// Fixed, documented ranges: 0, 1, 2–3, 4–7, and 8+ completed lessons.
export function activityLevel(count) {
  if (!validCount(count)) throw new Error('Invalid activity count')
  if (count === 0) return 0
  if (count === 1) return 1
  if (count <= 3) return 2
  if (count <= 7) return 3
  return 4
}

export function buildActivityGrid(activity, language = 'en') {
  const start = dateValue(activity.start_date)
  const end = dateValue(activity.end_date)
  if (end - start !== 364 * DAY) throw new Error('Invalid activity window')
  const counts = new Map(activity.daily_counts.map((day) => [day.date, day.count]))
  // Monday is row zero. UTC arithmetic represents date-only strings without DST drift.
  const offset = (new Date(start).getUTCDay() + 6) % 7
  const gridStart = start - offset * DAY
  const weekCount = Math.ceil((365 + offset) / 7)
  const weeks = Array.from({ length: weekCount }, (_, week) => Array.from({ length: 7 }, (_, row) => {
    const value = gridStart + (week * 7 + row) * DAY
    if (value < start || value > end) return null
    const date = new Date(value).toISOString().slice(0, 10)
    const count = counts.get(date) || 0
    return { date, count, level: activityLevel(count) }
  }))
  const monthFormat = new Intl.DateTimeFormat(language, { month: 'short', timeZone: 'UTC' })
  const months = []
  for (let value = start; value <= end; value += DAY) {
    const date = new Date(value)
    if (value === start || date.getUTCDate() === 1) {
      const column = Math.floor((value - gridStart) / (7 * DAY))
      // Avoid overlapping labels at the partial first/last weeks.
      if (months.length && column - months.at(-1).column < 3) months.pop()
      if (weekCount - column >= 2) months.push({ column, label: monthFormat.format(date) })
    }
  }
  return { weeks, months }
}
