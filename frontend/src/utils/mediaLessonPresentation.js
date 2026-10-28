// Presentation for source imports with exact, ordered heading metadata.
// No course IDs, titles or copied educational prose are needed. Legacy section
// identifiers and lessons with custom interactions keep their existing renderer.
function tableRow(text) {
  const cells = text.split('; ')
  if (cells.length < 2) return null
  const pairs = cells.map(cell => /^([^:;\n]{1,80}): (\S[^;\n]*)$/u.exec(cell))
  if (pairs.some(pair => !pair)) return null
  const headers = pairs.map(pair => pair[1])
  if (new Set(headers).size !== headers.length) return null
  return { headers, values: pairs.map(pair => pair[2]) }
}

function readingBlocks(paragraphs) {
  const blocks = []
  for (let index = 0; index < paragraphs.length;) {
    const first = tableRow(paragraphs[index])
    let end = index + 1
    const rows = first ? [first.values] : []
    if (first) {
      while (end < paragraphs.length) {
        const next = tableRow(paragraphs[end])
        if (!next || JSON.stringify(next.headers) !== JSON.stringify(first.headers)) break
        rows.push(next.values)
        end++
      }
    }
    // Require repeated column labels and lossless reconstruction. Ambiguous
    // or isolated labelled prose is left untouched rather than guessed.
    if (rows.length >= 2) {
      blocks.push({ type: 'table', headers: first.headers, rows })
      index = end
    } else {
      const text = paragraphs[index++]
      const kind = /^(?:Важно:|Правило курса:)/u.test(text) ? 'warning'
        : /^[^—\n]{1,60} — /u.test(text) ? 'definition'
          : /^(?:Пример .*запроса:|«)/u.test(text) ? 'prompt' : 'paragraph'
      blocks.push({ type: 'paragraph', kind, text })
    }
  }
  return blocks
}

export function mediaLessonSections(lesson) {
  const content = lesson?.learning_content
  const headings = content?.source_sections
  if (!Array.isArray(headings) || !headings.length || headings.some(h => typeof h !== 'string' || !h.trim())
    || new Set(headings).size !== headings.length || content.interactions?.some(item => item.type !== 'image_placement')) return null
  const paragraphs = (lesson.text_content || '').split(/\n\s*\n/u).map(text => text.trim()).filter(Boolean)
  const positions = headings.map(heading => paragraphs.indexOf(heading))
  if (positions[0] !== 0 || positions.some((position, i) => position < 0
    || (i > 0 && position <= positions[i - 1])
    || paragraphs.filter(text => text === headings[i]).length !== 1)) return null
  return headings.map((heading, index) => {
    const paragraphsInSection = paragraphs.slice(positions[index] + 1, positions[index + 1] ?? paragraphs.length)
    const kind = /(?:Практика|практика|задание)/u.test(heading) ? 'practice'
      : /(?:пример|случай)/u.test(heading) ? 'example' : 'reading'
    return { heading, kind, blocks: readingBlocks(paragraphsInSection) }
  })
}
