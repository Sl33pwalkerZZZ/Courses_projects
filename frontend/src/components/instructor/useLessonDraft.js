import { useCallback, useContext, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { UNSAFE_NavigationContext } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { draftEqual, lessonDraft, savedDraft, guardStudioNavigation } from '../../utils/studioDraft'

export function useLessonDraft(lesson, language) {
  const [form, updateForm] = useState(() => lessonDraft(lesson, language))
  const [baseline, setBaseline] = useState(form)
  const current = useRef(form)
  const setForm = value => {
    current.current = typeof value === 'function' ? value(current.current) : value
    updateForm(current.current)
  }
  const acceptSave = (submitted, response) => {
    const next = savedDraft(current.current, submitted, response, language)
    setBaseline(next.baseline)
    setForm(next.form)
  }
  return { form, setForm, dirty: !draftEqual(form, baseline), acceptSave }
}

export function useDirtyLessonGuard(dirty) {
  const { navigator } = useContext(UNSAFE_NavigationContext)
  const { t } = useTranslation()
  const latest = useRef(() => true)
  useLayoutEffect(() => { latest.current = () => !dirty || window.confirm(t('instructorStudio.discardLessonChanges')) }, [dirty, t])
  useEffect(() => guardStudioNavigation(navigator, window, () => latest.current()), [navigator])
  useEffect(() => {
    const unload = event => {
      if (!dirty) return
      event.preventDefault()
      event.returnValue = ''
    }
    window.addEventListener('beforeunload', unload)
    return () => window.removeEventListener('beforeunload', unload)
  }, [dirty])
  return useCallback(() => latest.current(), [])
}
