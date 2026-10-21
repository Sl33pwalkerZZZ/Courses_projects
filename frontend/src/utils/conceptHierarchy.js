// Only this known source hierarchy may replace repeated definitions with
// relationship labels. Unrelated authored hierarchies retain the generic view.
export function isAiConceptHierarchy(items) {
  const titles = ['Искусственный интеллект', 'Машинное обучение', 'Глубокое обучение', 'LLM']
  return items.length === titles.length && items.every((item, index) => item?.title === titles[index])
}
