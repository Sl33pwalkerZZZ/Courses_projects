import { SourceParagraph } from './LearningContent'

export default function LessonResources({ paragraphs, language }) {
  if (!paragraphs.length) return null
  return <section className="lesson-resources" lang={language} aria-labelledby="lesson-resources-title">
    <h2 id="lesson-resources-title">{paragraphs[0]}</h2>
    <ul>{paragraphs.slice(1).map((text, index) => {
      const urls = [...text.matchAll(/https?:\/\/[^\s<>"]+/gu)]
      if (urls.length !== 1) return <li key={index}><SourceParagraph text={text} /></li>
      const url = urls[0][0].replace(/[),.;!?]+$/u, '')
      const label = text.slice(0, urls[0].index).replace(/[\s—–-]+$/u, '').trim()
      const trailing = text.slice(urls[0].index + url.length).trim()
      return <li key={index}><a href={url} target="_blank" rel="noopener noreferrer">{label || url}</a>{trailing && <span>{trailing}</span>}</li>
    })}</ul>
  </section>
}
