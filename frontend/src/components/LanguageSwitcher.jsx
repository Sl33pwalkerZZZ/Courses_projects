import { useTranslation } from 'react-i18next'

const LANGUAGES = [
  { code: 'ru', label: 'RU', name: 'Русский' },
  { code: 'kk', label: 'KZ', name: 'Қазақша' },
  { code: 'en', label: 'EN', name: 'English' },
]

export default function LanguageSwitcher() {
  const { t, i18n } = useTranslation()

  return (
    <div className="language-switcher" role="group" aria-label={t('header.language')}>
      {LANGUAGES.map((language) => (
        <button key={language.code} type="button" data-language={language.code}
          lang={language.code} aria-label={language.name} title={language.name}
          aria-pressed={i18n.resolvedLanguage === language.code}
          onClick={() => i18n.changeLanguage(language.code)}>
          {language.label}
        </button>
      ))}
    </div>
  )
}
