const headings = new Set([
  '1.1. Что такое искусственный интеллект',
  '1.2. Как работает современная языковая модель',
  '1.3. Чем отличается ИИ-модель от ИИ-сервиса',
  '1.4. Виды нейросетей и области применения',
  '1.5. Обзор популярных ИИ-сервисов',
  '1.6. Как правильно выбрать модель или сервис',
  '1.7. Практическая работа: выбор ИИ под собственную задачу',
  '1.8. Выводы по первой главе',
])

// Only verified chapter headings in this course; never normalize list numbers.
export function studentSourceHeading(text, lesson) {
  return lesson?.course_slug === 'kak-vybrat-neyroset-pod-svoyu-zadachu'
    && Number(lesson.id) >= 91 && Number(lesson.id) <= 96 && headings.has(text)
    ? text.replace(/^1\.[1-8]\. /u, '') : text
}
