import { getCourse8Reading } from '../../utils/course8Reading.js'
import './course8-reading.css'

function SourceTable({ headers, rows }) {
  return <div className="course8-table"><table><thead><tr>{headers.map(header => <th key={header} scope="col">{header}</th>)}</tr></thead>
    <tbody>{rows.map((row, index) => <tr key={index}>{row.map((cell, column) => <td key={column}>{cell}</td>)}</tr>)}</tbody>
  </table></div>
}

// Only replaces the verified reading/interactions, not objectives, assignments,
// images, permissions, completion or assessments managed by LessonView.
export default function Course8Reading({ lesson }) {
  const reading = getCourse8Reading(lesson)
  if (!reading) return null
  return <div className="course8-reading" lang="ru">
    <h2>{reading.heading}</h2>
    {reading.id === 93 && <>
      <p>{reading.definition}</p>
      <div className="course8-model-example"><strong>GPT → ChatGPT</strong><p>{reading.example}</p></div>
      <SourceTable headers={reading.comparison.headers} rows={reading.comparison.rows} />
      <p>{reading.conclusion}</p>
    </>}
    {reading.id === 94 && <>
      <SourceTable headers={reading.categories.headers} rows={reading.categories.rows} />
      <p>{reading.caveat}</p>
      <h2>{reading.servicesHeading}</h2>
      <div className="course8-services">{reading.services.map(service => <section key={service.title}>
        <h3>{service.title}</h3><p>{service.text}</p>
        <a href={service.url} target="_blank" rel="noopener noreferrer">{service.url}</a>
      </section>)}</div>
      <p className="course8-service-note">Доступные функции сервисов могут меняться. Проверяйте актуальные условия на официальных сайтах.</p>
      <p>{reading.conclusion}</p>
    </>}
    {reading.id === 95 && <ol className="course8-selection-steps">{reading.process.steps.map((step, index) => <li key={step.title}>
      <span className="course8-step-number" aria-hidden="true">{index + 1}</span>
      <div><h3>{step.title.replace(/^Шаг \d\.\s*/, '')}</h3>
        {index === 1 ? <SourceTable headers={reading.process.headers} rows={reading.process.rows} />
          : index === 2 ? <ul className="course8-criteria">{reading.process.criteria.map(criterion => <li key={criterion}>{criterion}</li>)}</ul>
            : <p>{step.text}</p>}
      </div>
    </li>)}</ol>}
  </div>
}
