import { useEffect, useId, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ArrowUp, MessageCircle, X } from 'lucide-react'
import api, { getAuthSession } from '../../api'
import { AI_GUIDE_QUESTION_LIMIT, createGuideRequest, guideErrorKey } from '../../utils/aiGuide'
import './AIGuide.css'

export default function AIGuide({ lessonId, initialOpen = false }) {
  const { t, i18n } = useTranslation()
  const panelId = useId()
  const inputId = useId()
  const [open, setOpen] = useState(initialOpen)
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const request = useRef(null)
  const input = useRef(null)
  const toggle = useRef(null)

  useEffect(() => () => request.current?.cancel(), [])
  useEffect(() => { if (open) input.current?.focus({ preventScroll: true }) }, [open])

  function clear() {
    request.current?.cancel()
    request.current = null
    setMessages([])
    setQuestion('')
    setLoading(false)
    setError('')
  }

  function close() {
    setOpen(false)
    toggle.current?.focus({ preventScroll: true })
  }

  async function send(event) {
    event.preventDefault()
    if (request.current || !question.trim() || question.trim().length > AI_GUIDE_QUESTION_LIMIT) return
    const text = question.trim()
    const current = createGuideRequest(api, {
      lessonId, question: text, language: i18n.resolvedLanguage?.split('-')[0],
      getGeneration: () => getAuthSession().generation,
    })
    request.current = current
    setLoading(true)
    setError('')
    try {
      const answer = await current.result
      if (request.current !== current) return
      setMessages(previous => [...previous.slice(-18), { question: text, answer }])
      setQuestion('')
    } catch (failure) {
      if (request.current === current && failure.name !== 'AbortError' && failure.code !== 'ERR_CANCELED') setError(guideErrorKey(failure))
    } finally {
      if (request.current === current) {
        request.current = null
        setLoading(false)
      }
    }
  }

  return <section className="ai-guide" aria-label={t('aiGuide.title')}>
    <button className="academic-button secondary ai-guide-toggle" type="button" ref={toggle}
      aria-expanded={open} aria-controls={panelId} onClick={() => open ? close() : setOpen(true)}>
      <MessageCircle size={18} aria-hidden="true" />{t('aiGuide.title')}
    </button>
    {open && <div className="ai-guide-panel" id={panelId}>
      <div className="ai-guide-header"><h2>{t('aiGuide.title')}</h2>
        <button type="button" className="academic-button secondary" aria-label={t('aiGuide.close')} onClick={close}><X size={18} aria-hidden="true" /></button>
      </div>
      <p className="ai-guide-note">{t('aiGuide.description')}</p>
      <div className="ai-guide-messages" role="log" aria-label={t('aiGuide.conversation')} aria-live="polite" aria-relevant="additions">
        {!messages.length && <p className="ai-guide-note">{t('aiGuide.empty')}</p>}
        {messages.map((message, index) => <div className="ai-guide-turn" key={index}>
          <p><strong>{t('aiGuide.you')}</strong>{message.question}</p>
          <p><strong>{t('aiGuide.answer')}</strong>{message.answer}</p>
        </div>)}
      </div>
      <form onSubmit={send} aria-busy={loading}>
        <label htmlFor={inputId}>{t('aiGuide.question')}</label>
        <textarea id={inputId} ref={input} rows={3} maxLength={AI_GUIDE_QUESTION_LIMIT} value={question}
          disabled={loading} onChange={event => setQuestion(event.target.value)} placeholder={t('aiGuide.placeholder')} />
        <div className="ai-guide-actions">
          <button className="academic-button secondary" type="button" onClick={clear} disabled={!messages.length && !question && !loading && !error}>{t('aiGuide.clear')}</button>
          <button className="academic-button" type="submit" disabled={loading || !question.trim()}><ArrowUp size={17} aria-hidden="true" />{t(loading ? 'aiGuide.loading' : 'aiGuide.send')}</button>
        </div>
        {loading && <p role="status" className="ai-guide-note">{t('aiGuide.loading')}</p>}
        {error && <p role="alert" className="error">{t(error)}</p>}
      </form>
    </div>}
  </section>
}
