import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync } from 'node:fs'
const source = path => readFileSync(new URL('../src/'+path, import.meta.url),'utf8')
test('liquid environment is decorative and pauses for hidden documents and reduced motion',()=>{
 const jsx=source('components/landing/LiquidEnvironment.jsx'),css=source('components/landing/LiquidEnvironment.css')
 assert.match(jsx,/aria-hidden="true"/);assert.match(jsx,/document\.hidden/)
 assert.match(jsx,/removeEventListener\('visibilitychange'/)
 assert.match(jsx,/cancelAnimationFrame\(frame\)/);assert.match(jsx,/!document\.hidden && !reducedMode/)
 assert.match(css,/prefers-reduced-motion:reduce/);assert.match(css,/animation: none/);assert.match(jsx,/reduced\.addEventListener\('change'/)
 assert.doesNotMatch(jsx,/Math\.random|getContext\(['"]webgl/)
})
test('floating surfaces have opaque fallback before feature-detected blur',()=>{
 const css=source('styles/liquid-surfaces.css')
 assert.ok(css.indexOf('background: var(--v2-surface)')<css.indexOf('@supports'))
 assert.match(css,/@supports.*backdrop-filter/);assert.match(css,/background: var\(--glass-floating\)/)
 assert.match(css,/studio-command-shell--overview/)
})
test('bounded hero parallax is independent of idle ASCII and respects input preferences',()=>{
 const hero=source('hooks/useHeroDepth.js'),ascii=source('components/landing/AsciiLearning.jsx')
 assert.match(hero,/reduced \|\| mobile/);assert.match(hero,/passive: true/)
 assert.match(hero,/Math\.max\(-32, Math\.min\(12/)
 assert.match(hero,/removeEventListener\('scroll'/)
 assert.doesNotMatch(ascii,/addEventListener\('scroll'|asciiScrollProgress/)
})
test('glass text retains AA contrast over full-strength environment colors',()=>{
 const css=source('styles/v2-tokens.css')
 const linear=c=>{c/=255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4}
 const lum=rgb=>rgb.map(linear).reduce((sum,c,i)=>sum+c*[.2126,.7152,.0722][i],0)
 const contrast=(a,b)=>{const [lo,hi]=[lum(a),lum(b)].sort((x,y)=>x-y);return(hi+.05)/(lo+.05)}
 const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16))
 for(const [name,block,glass,alpha]of [['dark',css.split(':root {')[1],[18,28,40],.68],['light',css.split(':root[data-theme="light"] {')[1],[250,252,254],.68]]){
  const colors=Object.fromEntries([...block.split('}')[0].matchAll(/--v2-([\w-]+): (#[\da-fA-F]{6});/g)].map(m=>[m[1],m[2]]))
  for(const underneath of [colors.canvas,name==='dark'?'#3D9FAD':'#A1C9D7',name==='dark'?'#286775':'#A9DBD9']){
   const effective=glass.map((c,i)=>c*alpha+rgb(underneath)[i]*(1-alpha))
   for(const key of ['text','text-muted','link'])assert.ok(contrast(rgb(colors[key]),effective)>=4.5,`${name} ${key}`)
  }
 }
})
