export const selectionFields = ['working_task', 'input_data', 'expected_result', 'required_capabilities', 'final_justification']
export const comparisonCriteria = ['quality', 'features', 'cost', 'speed', 'privacy', 'ease']
export function emptySelectionMap() {
  return { working_task: '', input_data: '', expected_result: '', required_capabilities: '', data_classification: 'public', services: ['', ''], comparison_criteria: Object.fromEntries(comparisonCriteria.map(key => [key, ''])), testing_results: [], selected_service: '', final_justification: '' }
}
export function selectionMapProblems(payload) {
  payload = serializeSelectionMap(payload)
  const errors = selectionFields.filter(key => !payload[key]?.trim())
  const services = payload.services.map(value => value.trim()).filter(Boolean)
  if (services.length < 2 || services.length > 3 || new Set(services.map(value => value.toLowerCase())).size !== services.length) errors.push('services')
  if (!['public', 'internal', 'confidential'].includes(payload.data_classification)) errors.push('data_classification')
  if (comparisonCriteria.some(key => !payload.comparison_criteria[key]?.trim())) errors.push('comparison_criteria')
  if (!services.includes(payload.selected_service)) errors.push('selected_service')
  if (services.some(service => !payload.testing_results.some(row => row.service === service && row.result?.trim()))) errors.push('testing_results')
  return errors
}
export function updateComparedService(payload, index, value) {
  const previous = payload.services[index]
  return { ...payload, services: payload.services.map((service, i) => i === index ? value : service), selected_service: payload.selected_service === previous ? value : payload.selected_service,
    testing_results: payload.testing_results.map(row => row.service === previous ? { ...row, service: value } : row) }
}

// Editable empty slots stay in React; the backend receives only named services.
export function normalizeSelectionMap(saved = {}) {
  const initial = emptySelectionMap()
  const services = [...(saved.services || [])]
  while (services.length < 2) services.push('')
  return { ...initial, ...saved, services, comparison_criteria: { ...initial.comparison_criteria, ...saved.comparison_criteria } }
}
export function serializeSelectionMap(payload) {
  const services = payload.services.map(value => value.trim()).filter(Boolean)
  return { ...payload, services, selected_service: payload.selected_service.trim(), testing_results: payload.testing_results.filter(row => row.service.trim() && services.includes(row.service.trim())).map(row => ({ service: row.service.trim(), result: row.result })) }
}
