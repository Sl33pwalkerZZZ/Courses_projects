import assert from 'node:assert/strict'
import { stat } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { relative, resolve } from 'node:path'
import test from 'node:test'
import { createTestServer } from './helpers/vite.mjs'

test('SSR fixtures use separate temporary caches and remove only those caches', async () => {
  const first = await createTestServer()
  let second
  try {
    second = await createTestServer()
    assert.notEqual(first.cacheDir, second.cacheDir)
    for (const fixture of [first, second]) {
      assert.ok(!relative(tmpdir(), fixture.cacheDir).startsWith('..'))
      assert.notEqual(fixture.cacheDir, resolve('node_modules/.vite'))
      assert.ok((await stat(fixture.cacheDir)).isDirectory())
      const hero = await fixture.ssrLoadModule('/src/components/HomeHero.jsx')
      assert.equal(typeof hero.default, 'function')
    }
  } finally {
    await first.close()
    await second?.close()
  }
  for (const fixture of [first, second]) {
    await assert.rejects(stat(fixture.cacheDir), { code: 'ENOENT' })
  }
})
