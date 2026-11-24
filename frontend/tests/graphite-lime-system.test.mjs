import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
const root = new URL('../', import.meta.url)
const css = readFileSync(new URL('src/styles/v2-tokens.css', root), 'utf8')
function contrast(a, b) {
  const luminance = hex => [1,3,5].map(i => parseInt(hex.slice(i,i+2),16)/255).map(c => c <= .04045 ? c/12.92 : ((c+.055)/1.055)**2.4).reduce((v,c,i) => v+c*[.2126,.7152,.0722][i],0)
  const [lo,hi] = [luminance(a),luminance(b)].sort((x,y)=>x-y)
  return (hi+.05)/(lo+.05)
}
for (const [name, block] of [['dark',css.split(':root {')[1]],['light',css.split(':root[data-theme="light"] {')[1]]]) {
  const colors = Object.fromEntries([...block.split('}')[0].matchAll(/--v2-([\w-]+): (#[\da-fA-F]{6});/g)].map(m=>[m[1],m[2]]))
  test(`${name}: focus, disabled, status and active-state contrast`, () => {
    for (const bg of ['canvas','surface','surface-raised']) {
      assert.ok(contrast(colors.focus,colors[bg])>=3,`focus/${bg}`)
      assert.ok(contrast(colors.info,colors[bg])>=4.5,`info/${bg}`)
    }
    for (const state of ['success','warning','danger','info']) assert.ok(contrast(colors[state],colors[`${state}-surface`])>=4.5,state)
    assert.ok(contrast(colors['disabled-text'],colors['disabled-bg'])>=4.5)
    assert.ok(contrast(colors['on-primary'],colors['primary-active'])>=4.5)
    for (const fill of ['danger-fill','danger-fill-hover']) assert.ok(contrast(colors['on-danger'],colors[fill])>=4.5)
    assert.ok(contrast(colors.progress,colors['surface-raised'])>=3)
  })
}
const provenance = JSON.parse(readFileSync(new URL('public/fonts/provenance.json', root)))
for (const family of ['noto_sans','ibm_plex_mono']) {
  test(`${family}: shipped files match provenance and license notice exists`, () => {
    for (const entry of provenance[family].files) {
      const bytes=readFileSync(new URL(`public/fonts/${entry.local_file || entry.file}`,root))
      assert.equal(bytes.length,entry.size)
      assert.equal(createHash('sha256').update(bytes).digest('hex'),entry.sha256)
    }
    assert.match(readFileSync(new URL(`public/fonts/${family==='noto_sans'?'NotoSans':'IBMPlexMono'}-OFL.txt`,root),'utf8'),/SIL OPEN FONT LICENSE/)
  })
  test(`${family}: actual font cmap covers RU, KK and EN`, context => {
    let charset
    try { charset=provenance[family].files.filter(f=>/\.(woff2|ttf)$/.test(f.file)).map(f=>execFileSync('fc-query',['--format=%{charset}\n',new URL(`public/fonts/${f.local_file || f.file}`,root).pathname],{encoding:'utf8'})).join(' ') }
    catch(error) { if(error.code==='ENOENT'){context.skip('fontconfig not installed; byte integrity remains verified');return} throw error }
    const ranges=charset.trim().split(/\s+/).map(x=>x.split('-').map(v=>parseInt(v,16)))
    for(const char of provenance[family].tested) assert.ok(ranges.some(([a,b=a])=>char.codePointAt(0)>=a&&char.codePointAt(0)<=b),`missing ${char}`)
  })
}
test('local specimen is outside production routing and uses real shared controls',()=>{
 const fixture=readFileSync(new URL('tests/fixtures/design-system/main.jsx',root),'utf8')
 for(const component of ['Button','Badge','Surface','Dialog','ThemeToggle']) assert.match(fixture,new RegExp(`import ${component} from`))
 assert.match(fixture,/ru: /);assert.match(fixture,/kk: /);assert.match(fixture,/en: /)
 assert.doesNotMatch(readFileSync(new URL('src/App.jsx',root),'utf8'),/fixtures\/design-system/)
})
