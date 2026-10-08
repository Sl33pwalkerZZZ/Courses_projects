export function latestCourseApplication(applications, slug) {
  return applications.filter((application) => application.course.slug === slug)
    .sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at) || b.id - a.id)[0] || null
}

export async function loadCourseEnrollment(client, slug, requiresApproval) {
  const [enrollments, applications] = await Promise.allSettled([
    client.get('/my/enrollments/'),
    requiresApproval ? client.get('/my/enrollment-requests/') : Promise.resolve({ data: [] }),
  ])
  if (enrollments.status === 'rejected') throw enrollments.reason
  const enrollment = enrollments.value.data.find((item) => item.course.slug === slug) || null
  // Application history is optional for someone whose access is already confirmed.
  if (applications.status === 'rejected' && !enrollment) throw applications.reason
  return {
    enrollment,
    application: applications.status === 'fulfilled' ? latestCourseApplication(applications.value.data, slug) : null,
  }
}

export function enrollmentErrorKey(error, fallback = 'enrollment.submitError') {
  if (error.response?.status === 401) return 'enrollment.sessionExpired'
  const code = error.response?.data?.code
  if (code === 'duplicate_pending') return 'enrollment.duplicatePending'
  if (code === 'already_enrolled') return 'enrollment.alreadyEnrolled'
  if (code === 'open_enrollment' || code === 'approval_required') return 'enrollment.policyChanged'
  if (error.response?.data?.message) return 'enrollment.messageError'
  return fallback
}
