import { useId } from 'react'
import { SourceParagraph, SourceTable } from './LearningContent'
import './mediaLessonReading.css'

export default function MediaLessonReading({ sections }) {
  const id = useId()
  return <div className="media-lesson-reading">{sections.map((section, index) => {
    const labelId = `${id}-${index}`
    return <section key={section.heading} className={`media-lesson-section media-lesson-section--${section.kind}`} aria-labelledby={labelId}>
      <h2 id={labelId}>{section.heading}</h2>
      {section.blocks.map((block, blockIndex) => block.type === 'table'
        ? <SourceTable key={blockIndex} headers={block.headers} rows={block.rows} labelId={labelId} />
        : <div key={blockIndex} className={block.kind === 'paragraph' ? undefined : `media-lesson-${block.kind}`}>
          <SourceParagraph text={block.text} />
        </div>)}
    </section>
  })}</div>
}
