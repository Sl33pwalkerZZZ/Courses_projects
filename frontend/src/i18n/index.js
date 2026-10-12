import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import { readPreference, savePreference } from '../utils/preferences'
import ru from './locales/ru.json'
import kk from './locales/kk.json'
import en from './locales/en.json'

const LANGUAGE_KEY = 'ai-courses-language'
const languages = ['ru', 'kk', 'en']
const savedLanguage = readPreference(LANGUAGE_KEY)

// Bundle these small dictionaries locally; language changes need no API calls.
i18n.use(initReactI18next).init({
  resources: { ru: { translation: ru }, kk: { translation: kk }, en: { translation: en } },
  lng: languages.includes(savedLanguage) ? savedLanguage : 'ru',
  fallbackLng: 'ru',
  supportedLngs: languages,
  initImmediate: false,
  interpolation: { escapeValue: false },
})

function updateDocument(language) {
  document.documentElement.lang = language
  document.title = i18n.t('meta.title')
  document.querySelector('meta[name="description"]')?.setAttribute('content', i18n.t('meta.description'))
}

updateDocument(i18n.language)
i18n.on('languageChanged', (language) => {
  savePreference(LANGUAGE_KEY, language)
  updateDocument(language)
})

export default i18n
