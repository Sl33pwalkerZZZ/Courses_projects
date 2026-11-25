import assert from 'node:assert/strict'
import {test} from 'node:test'
import{readFileSync}from'node:fs'
import{createRefractionPixels,allowSvgOptics}from'../src/utils/glassOptics.js'
test('original edge map preserves neutral centre and points opposing edges in opposite directions',()=>{
 const n=128,a=createRefractionPixels(n),at=(x,y)=>[...a.slice((y*n+x)*4,(y*n+x)*4+4)]
 assert.deepEqual(at(64,64),[128,128,128,255]);assert.deepEqual(a,createRefractionPixels(n))
 assert.ok(at(0,64)[0]<40);assert.ok(at(127,64)[0]>215)
 assert.ok(at(64,0)[1]<40);assert.ok(at(64,127)[1]>215)
 for(let i=3;i<a.length;i+=4)assert.equal(a[i],255)
})
test('SVG visual enhancement conservatively excludes Firefox, mobile, low-core and reduced-motion',()=>{
 assert.equal(allowSvgOptics({userAgent:'Chrome/158.0',cores:8}),true)
 for(const input of [{userAgent:'Firefox/143.0'},{userAgent:'Version/18.0 Safari/605.1'},{userAgent:'Chrome/158.0',mobile:true},{userAgent:'Chrome/158.0',reduced:true},{userAgent:'Chrome/158.0',cores:4}])assert.equal(allowSvgOptics(input),false)
})
test('four material roles retain fallback and avoid repeated Studio backdrop filters',()=>{
 const css=readFileSync(new URL('../src/styles/glass-materials.css',import.meta.url),'utf8')
 for(const role of ['a','b','c','d'])assert.match(css,new RegExp('--material-'+role+':'))
 assert.ok(css.indexOf('background:var(--v2-surface)')<css.indexOf('@supports'))
 assert.match(css,/glass-workspace :is\([^}]+backdrop-filter:none; -webkit-backdrop-filter:none/s)
 assert.match(css,/data-glass-optics="svg"/);assert.match(css,/prefers-reduced-transparency:reduce/)
 assert.match(css,/lesson-reading-area/)
 const optics=readFileSync(new URL('../src/components/GlassOptics.jsx',import.meta.url),'utf8')
 assert.match(optics,/scale="14"/);assert.doesNotMatch(optics,/feTurbulence|setInterval|requestAnimationFrame/)
 assert.match(optics,/removeEventListener/)
})

test('material text retains AA against conservative full-strength light-field backgrounds',()=>{
 const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));const luminance=v=>v.reduce((s,c,i)=>{c/=255;return s+(c<=.04045?c/12.92:((c+.055)/1.055)**2.4)*[.2126,.7152,.0722][i]},0)
 const ratio=(a,b)=>{const[x,y]=[luminance(a),luminance(b)].sort((a,b)=>a-b);return(y+.05)/(x+.05)}
 for(const[fill,ink,backgrounds]of[['#121c28','#c2d1dd',['#0b1017','#3e848e']],['#fafcfe','#344d60',['#eef2f5','#a6c3d5']]])for(const alpha of[.38,.48,.96])for(const bg of backgrounds){
  const effective=rgb(fill).map((v,i)=>v*alpha+rgb(bg)[i]*(1-alpha));assert.ok(ratio(rgb(ink),effective)>=4.5,`${fill} ${alpha} ${bg}`)
 }
})
