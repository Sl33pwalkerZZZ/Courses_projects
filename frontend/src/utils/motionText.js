// Older browsers without Segmenter keep a whole word intact instead of splitting
// a combining sequence, emoji or Kazakh grapheme incorrectly.
export function graphemes(text, language = 'en') {
  return typeof Intl.Segmenter === 'function'
    ? [...new Intl.Segmenter(language, { granularity: 'grapheme' }).segment(text)].map((part) => part.segment)
    : [text]
}
export function textWords(text) {
  return text.split(/(\s+)/u).filter(Boolean)
}
