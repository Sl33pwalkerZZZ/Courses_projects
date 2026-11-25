import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ASCII_COLUMNS, ASCII_ROWS, STATIC_ASCII_FRAME, createAsciiFrame } from '../src/utils/asciiLearning.js'

test('sculpture frames remain bounded and dense throughout rotation', () => {
  for (const time of [0, 2.8, 7, 14, 25, 60]) {
    const rows = createAsciiFrame(time).split('\n')
    assert.equal(rows.length, ASCII_ROWS)
    assert.ok(rows.every((row) => row.length === ASCII_COLUMNS))
    assert.ok(rows.join('').replace(/\s/g, '').length > 500)
    assert.equal(rows[0].trim(), '')
    assert.equal(rows.at(-1).trim(), '')
    assert.ok(rows.every((row) => row[0] === ' ' && row.at(-1) === ' '))
  }
})
test('elapsed time drives deterministic motion without a scroll dependency', () => {
  assert.equal(createAsciiFrame(2.8), STATIC_ASCII_FRAME)
  assert.equal(createAsciiFrame(3), createAsciiFrame(3))
  assert.notEqual(createAsciiFrame(0), createAsciiFrame(1))
  assert.notEqual(createAsciiFrame(1), createAsciiFrame(8))
  assert.equal(createAsciiFrame(NaN), createAsciiFrame(0))
  assert.equal(createAsciiFrame(Infinity), createAsciiFrame(0))
})
test('surface uses multiple luminance characters rather than a wire outline', () => {
  const characters = new Set(STATIC_ASCII_FRAME.replace(/\s/g, ''))
  assert.ok(characters.size >= 7)
  assert.ok([...characters].every((character) => '.,:;=+*#%@'.includes(character)))
})
