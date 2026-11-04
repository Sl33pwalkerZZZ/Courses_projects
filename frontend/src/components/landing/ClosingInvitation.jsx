import { ArrowUpRight, ArrowDown } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Button from '../ui/Button'
import Reveal from '../Reveal'

export default function ClosingInvitation() {
  const { t } = useTranslation()
  return <Reveal><section className="cinema-closing" aria-labelledby="cinema-closing-title">
    <p className="cinema-kicker">AI Courses</p><h2 id="cinema-closing-title">{t('cinema.closingTitle')}</h2>
    <p>{t('cinema.closingDescription')}</p><div className="cinema-closing-actions">
      <Button href="#course-library">{t('catalog.explore')}<ArrowDown size={18} aria-hidden="true" /></Button>
      <Button to="/register" variant="secondary">{t('catalog.start')}<ArrowUpRight size={18} aria-hidden="true" /></Button>
    </div>
  </section></Reveal>
}
