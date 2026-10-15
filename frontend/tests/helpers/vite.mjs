import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createServer } from 'vite'

// Every SSR test gets its own cache. The default node_modules/.vite cache
// belongs to the running development server and must not be invalidated here.
export async function createTestServer() {
  const cacheDir = await mkdtemp(join(tmpdir(), 'ai-courses-ssr-test-'))
  let server
  try {
    server = await createServer({
      cacheDir,
      server: { middlewareMode: true, hmr: false, ws: false },
      optimizeDeps: { noDiscovery: true, include: [] },
      appType: 'custom',
    })
  } catch (error) {
    await rm(cacheDir, { recursive: true, force: true })
    throw error
  }

  return {
    cacheDir,
    ssrLoadModule: (...args) => server.ssrLoadModule(...args),
    async close() {
      try {
        await server.close()
      } finally {
        await rm(cacheDir, { recursive: true, force: true })
      }
    },
  }
}
