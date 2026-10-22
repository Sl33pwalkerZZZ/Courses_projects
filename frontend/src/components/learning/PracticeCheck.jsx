import { useId, useState } from 'react'
import { useTranslation } from 'react-i18next'

const checks = {
  93: { question: 'Коллеге нужен готовый интерфейс для работы с ИИ без программирования. Что стоит сравнить сначала?', choices: ['Готовые ИИ-сервисы', 'Только архитектуру моделей'], answer: 0, explanation: 'Сервис предоставляет интерфейс и рабочие функции. Удобно сначала выбрать подходящий сервис, затем модель, если такая настройка доступна.' },
  95: { question: 'Вы проверили два сервиса на разных данных и получили разные результаты. Как сделать сравнение полезнее?', choices: ['Повторить проверку на одинаковых обезличенных данных', 'Выбрать самый длинный ответ'], answer: 0, explanation: 'Одинаковые исходные данные позволяют сопоставить результаты. Проверяйте полноту, точность, удобство, скорость и фактические ошибки; учитывайте требования к защите данных.' },
}

// Optional local practice: no API, persistence, grading or completion effects.
export default function PracticeCheck({ lessonId }) {
  const { t } = useTranslation()
  const id = useId()
  const [selected, setSelected] = useState(null)
  const check = checks[lessonId]
  if (!check) return null
  return <section className="learning-interaction practice-check" aria-labelledby={`${id}-title`}>
    <h2 id={`${id}-title`}>{t('learning.selfCheck')}</h2>
    <p>{t('learning.selfCheckNote')}</p>
    <fieldset lang="ru"><legend>{check.question}</legend>
      {check.choices.map((choice, index) => <label key={choice}>
        <input type="radio" name={`${id}-answer`} checked={selected === index} onChange={() => setSelected(index)} />{choice}
      </label>)}
    </fieldset>
    {selected !== null && <div role="status"><strong>{t(selected === check.answer ? 'learning.practiceCorrect' : 'learning.practiceTryAgain')}</strong><p lang="ru">{check.explanation}</p></div>}
  </section>
}
