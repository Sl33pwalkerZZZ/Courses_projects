import { useId, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { selectionStepUsesSourceTable } from '../../utils/lessonPresentation.js'
import ConceptHierarchy from './ConceptHierarchy.jsx'
import { isAiConceptHierarchy } from '../../utils/conceptHierarchy.js'
import './learning.css'

export function SourceParagraph({ text }) {
  const parts = []
  let previous = 0
  for (const match of text.matchAll(/https?:\/\/[^\s<>"]+/gu)) {
    const url = match[0].replace(/[),.;!?]+$/u, '')
    parts.push(text.slice(previous, match.index))
    parts.push(<a key={match.index} href={url} target="_blank" rel="noopener noreferrer">{url}</a>)
    parts.push(match[0].slice(url.length))
    previous = match.index + match[0].length
  }
  parts.push(text.slice(previous))
  return <p>{parts}</p>
}

export function ContentLanguageNotice({ language }) {
  const { t, i18n } = useTranslation()
  return language === 'ru' && !i18n.language.startsWith('ru') ? <p className="learning-language" role="note">{t('learning.russianFallback')}</p> : null
}

function SourceTable({ headers = [], rows = [], labelId }) {
  return rows.length > 0 && <div className="learning-table-scroll" role="region" aria-labelledby={labelId} tabIndex={0}><table>
    {headers.length > 0 && <thead><tr>{headers.map((header, i) => <th key={i} scope="col">{header}</th>)}</tr></thead>}
    <tbody>{rows.map((row, i) => <tr key={i}>{(Array.isArray(row) ? row : Object.values(row)).map((cell, j) => <td key={j}>{String(cell ?? '')}</td>)}</tr>)}</tbody>
  </table></div>
}


export function LearningInteraction({ interaction }) {
  const { t } = useTranslation()
  const id = useId()
  const [selected, setSelected] = useState(0)
  const items = interaction.items || interaction.steps || interaction.cards || interaction.services || (interaction.type === 'categories' ? (interaction.rows || []).map(row => ({ title: row[0], text: row.slice(1).join(' — ') })) : [])
  const active = items[selected] || items[0]
  const isProcess = interaction.type === 'llm_steps'
  const isNestedHierarchy = interaction.type === 'concept_hierarchy' && isAiConceptHierarchy(items)
  const itemTitle = item => typeof item === 'string' ? item : item?.title || item?.name || item?.label || ''
  const itemText = item => typeof item === 'string' ? '' : item?.text || item?.description || item?.body || ''
  const hasTable = interaction.rows?.length > 0
  const tableInDetail = selectionStepUsesSourceTable(interaction, selected)
  if (!items.length && !hasTable && !interaction.description && !interaction.criteria?.length && !interaction.note && !interaction.warning) return null
  const sourceLink = active?.url && /^https?:\/\//i.test(active.url) ? active.url : null
  const isSteps = ['llm_steps', 'selection_steps', 'concept_hierarchy'].includes(interaction.type)
  return <section className={`learning-interaction learning-${interaction.type}`} aria-labelledby={`${id}-title`}>
    <h3 id={`${id}-title`}>{interaction.title}</h3>
    {interaction.description && <p>{interaction.description}</p>}
    {isNestedHierarchy && <ConceptHierarchy items={items} />}
    {isProcess && items.length > 0 && <>
      <ol className="learning-process">
        {items.map((item, index) => <li key={index}>
          <span className="learning-process-number" aria-hidden="true">{index + 1}</span>
          <div className="learning-process-copy">
            <h4>{itemTitle(item)}</h4>
            {itemText(item) && <p>{itemText(item)}</p>}
          </div>
        </li>)}
      </ol>
    </>}
    {!isProcess && !isNestedHierarchy && items.length > 0 && <>
      <div className="learning-choice-list" role="group" aria-label={t(isSteps ? 'learning.exploreSteps' : 'learning.exploreItems')}>
        {items.map((item, index) => <button key={index} type="button" aria-pressed={index === selected} aria-controls={`${id}-detail`}
          onClick={() => setSelected(index)}>{isSteps && <span aria-hidden="true">{index + 1}. </span>}{typeof item === 'string' ? item : item.title || item.name || item.label}</button>)}
      </div>
      <div id={`${id}-detail`} className="learning-detail" role="region" aria-labelledby={`${id}-title`} aria-live="polite" aria-atomic="true">
        {typeof active === 'string' ? <p>{active}</p> : <>
          <h4>{active?.title || active?.name || active?.label}</h4>
          {(active?.text || active?.description || active?.body) && <p>{active.text || active.description || active.body}</p>}
          {tableInDetail && <SourceTable headers={interaction.headers} rows={interaction.rows} labelId={`${id}-title`} />}
          {sourceLink && <a href={sourceLink} target="_blank" rel="noopener noreferrer">{sourceLink}</a>}
          {active?.details && <p>{active.details}</p>}
          {active?.examples?.length > 0 && <ul>{active.examples.map((example, i) => <li key={i}>{example}</li>)}</ul>}
        </>}
      </div>
    </>}
    {interaction.criteria?.length > 0 && <ul>{interaction.criteria.map((criterion, index) => <li key={index}>{criterion}</li>)}</ul>}
    {!tableInDetail && <SourceTable headers={interaction.headers} rows={interaction.rows} labelId={`${id}-title`} />}
    {interaction.note && <p className="learning-source-note">{interaction.note}</p>}
    {interaction.warning && <p className="learning-source-note">{interaction.warning}</p>}
  </section>
}

export default function LearningContent({ content, showLanguageNotice = true }) {
  const { t } = useTranslation()
  if (!content) return null
  return <section className="learning-content">
    {showLanguageNotice && <ContentLanguageNotice language={content.content_language} />}
    {content.objectives?.length > 0 && <section><h2>{t('learning.objectives')}</h2><ul lang={content.content_language || undefined}>{content.objectives.map((objective, i) => <li key={i}>{objective}</li>)}</ul></section>}
    {content.interactions?.map((interaction, i) => <div lang={content.content_language || undefined} key={i}><LearningInteraction interaction={interaction} /></div>)}
    {content.takeaways?.length > 0 && <section><h2>{t('learning.takeaways')}</h2><ul lang={content.content_language || undefined}>{content.takeaways.map((item, i) => <li key={i}>{item}</li>)}</ul></section>}
  </section>
}
