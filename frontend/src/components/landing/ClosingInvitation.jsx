import { ArrowUpRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Button from '../ui/Button'

export default function ClosingInvitation() {
  const { t } = useTranslation()
  return <section className="gl-closing" aria-labelledby="gl-closing-title"><h2 id="gl-closing-title">{t('landing.closingTitle')}</h2><div><p>{t('landing.closingDescription')}</p><div className="gl-closing-actions"><Button href="#course-library">{t('catalog.explore')}<ArrowUpRight size={18} aria-hidden="true"/></Button><Button to="/register" variant="secondary">{t('header.register')}</Button></div></div></section>
}
