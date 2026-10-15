import { Component } from 'react'
import { Compass, TriangleAlert } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Button from './ui/Button'

export function PageLoading() {
  const { t } = useTranslation()
  return <div className="play-page-loading" role="status" aria-busy="true"><p>{t('common.loading')}</p><div aria-hidden="true"><i /><i /><i /></div></div>
}

export function NotFound() {
  const { t } = useTranslation()
  return <section className="play-global-state"><Compass size={48} aria-hidden="true" /><p className="eyebrow">404</p><h1>{t('playground.notFound')}</h1><p>{t('playground.notFoundDescription')}</p><Button to="/">{t('header.catalog')}</Button></section>
}
function RenderFailure({ onRetry }) {
  const { t } = useTranslation()
  return <section className="play-global-state" role="alert"><TriangleAlert size={40} aria-hidden="true" /><h1>{t('playground.renderError')}</h1><p>{t('playground.renderErrorDescription')}</p><Button onClick={onRetry}>{t('common.retry')}</Button><Button href="/" variant="secondary">{t('header.catalog')}</Button></section>
}
export class PageErrorBoundary extends Component {
  state = { failed: false, resetKey: this.props.resetKey }
  static getDerivedStateFromError() { return { failed: true } }
  static getDerivedStateFromProps(props, state) {
    return props.resetKey !== state.resetKey ? { failed: false, resetKey: props.resetKey } : null
  }
  render() { return this.state.failed ? <RenderFailure onRetry={() => window.location.reload()} /> : this.props.children }
}
