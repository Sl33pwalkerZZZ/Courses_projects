import assert from 'node:assert/strict'
import {test} from 'node:test'
import {readFileSync} from 'node:fs'
const read=p=>readFileSync(new URL('../src/'+p,import.meta.url),'utf8')
test('all Studio routes share a stable workspace outlet without navigation-based remounts',()=>{
 const source=read('pages/instructor/InstructorStudio.jsx')
 assert.match(source,/className="studio-workspace glass-workspace"><Outlet context=\{\{ identity \}\}/)
 assert.doesNotMatch(source,/studio-workspace[^>]*key=/)
 const css=read('pages/instructor/studio-glass.css')
 assert.match(css,/\.studio-command-shell \{ display:grid/)
 assert.match(css,/grid-template-columns:248px minmax\(0,1fr\)/)
 assert.match(css,/max-width:2240px/)
 assert.match(css,/data-open=true/)
 assert.match(css,/prefers-reduced-motion:reduce/)
})
test('all Studio route permissions and mobile keyboard disclosure remain in existing navigation',()=>{
 const source=read('components/instructor/StudioNavigation.jsx')
 assert.match(source,/identity\.is_moderator/)
 assert.match(source,/identity\.can_manage_instructors/)
 assert.match(source,/aria-expanded=\{open\}/)
 assert.match(source,/event\.key === 'Escape'/)
 assert.match(source,/toggle\.current\?\.focus\(\)/)
})
