import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import { refreshInstructorPermissions } from '../../hooks/useInstructor'
import { studioError } from '../../utils/instructorStudio'

export function useStudioResource(path) {
  const [state, setState] = useState(null)
  const [revision, setRevision] = useState(0)
  const { t } = useTranslation()
  useEffect(() => {
    const controller = new AbortController()
    if (!path) return () => controller.abort()
    api.get(path, { signal: controller.signal }).then(({ data }) => {
      if (!controller.signal.aborted) setState({ path, revision, data, error: null })
    }).catch(error => {
      if (error.response?.status === 403) refreshInstructorPermissions()
      if (!controller.signal.aborted) setState({ path, revision, data: null, error })
    })
    return () => controller.abort()
  }, [path, revision])
  // Translate stored errors at render time. Language changes never refetch a
  // resource or unmount a dirty form. Obsolete path/revision results stay hidden.
  const current = state?.path === path && state?.revision === revision
  return { loading: Boolean(path) && !current, data: current ? state.data : null,
    error: current && state.error ? studioError(state.error, t('instructorStudio.loadError'), t) : '',
    reload: () => setRevision(value => value + 1) }
}

// Every mutation is aborted on unmount; the existing API client additionally
// rejects obsolete responses/retries when the authentication generation changes.
export function useStudioAction() {
  const { t } = useTranslation()
  const controller = useRef(null)
  const active = useRef(false)
  const running = useRef(false)
  const [state, setState] = useState({ busy: false, error: '', message: '' })
  useEffect(() => { active.current = true; return () => { active.current = false; controller.current?.abort() } }, [])
  async function run(work, onSuccess, successKey = 'instructorStudio.saved') {
    if (!active.current || running.current) return
    const request = new AbortController()
    controller.current = request
    running.current = true
    setState({ busy: true, error: '', message: '' })
    try {
      const result = await work(request.signal)
      if (request.signal.aborted || !active.current) return
      setState({ busy: false, error: '', message: successKey ? t(successKey) : '' })
      onSuccess?.(result.data)
    } catch (error) {
      if (error.response?.status === 403) refreshInstructorPermissions()
      if (!request.signal.aborted && active.current) setState({ busy: false, error: studioError(error, t('instructorStudio.saveError'), t), message: '' })
    } finally { running.current = false }
  }
  return { ...state, run }
}
