import LessonAttachment from './LessonAttachment'
import ProtectedLessonImage from '../ProtectedLessonImage'
import { useId } from 'react'
import { SourceParagraph, SourceTable } from './LearningContent'
import './mediaLessonReading.css'

export default function MediaLessonReading({ sections, placements = new Map(), attachments = new Map() }) {
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
      {(placements.get(section.heading) || []).map(({ image, caption }) => <figure className="lesson-inline-figure" key={image.id}>
        <ProtectedLessonImage image={image} enlarge />
        <figcaption>{caption}</figcaption>
      </figure>)}
      {(attachments.get(section.heading) || []).map(asset => <LessonAttachment asset={asset} key={asset.id} />)}
    </section>
  })}</div>
}
