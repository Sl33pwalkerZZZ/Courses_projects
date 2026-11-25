import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createLiquidPixels, LIQUID_QUALITY } from '../src/utils/liquidField.js'
import { readFileSync } from 'node:fs'
test('original liquid field changes shape over idle time deterministically in both themes', () => {
  for (const dark of [false,true]) {
    const first=createLiquidPixels(64,40,0,dark),later=createLiquidPixels(64,40,5,dark)
    assert.deepEqual(first,createLiquidPixels(64,40,0,dark))
    assert.notDeepEqual(first,later)
    let changed=0
    for(let i=0;i<first.length;i+=4){if(Math.max(...[0,1,2].map(c=>Math.abs(first[i+c]-later[i+c])))>3)changed++;assert.equal(first[i+3],255)}
    assert.ok(changed>64*40*.25)
  }
})
test('liquid renderer reuses its buffer and bounds work for mobile',()=>{
 const buffer=new Uint8ClampedArray(8*6*4)
 assert.equal(createLiquidPixels(8,6,10,true,buffer),buffer)
 assert.ok(LIQUID_QUALITY.mobile.width*LIQUID_QUALITY.mobile.height<LIQUID_QUALITY.desktop.width*LIQUID_QUALITY.desktop.height)
 assert.equal(LIQUID_QUALITY.mobile.fps,12)
})
test('decorative liquid lifecycle cancels RAF and listens to visibility, preferences and theme',()=>{
 const source=readFileSync(new URL('../src/components/landing/LiquidEnvironment.jsx',import.meta.url),'utf8')
 for(const requirement of [/aria-hidden="true"/,/document.hidden/,/cancelAnimationFrame/,/reducedMode/,/removeEventListener\('visibilitychange'/,/attributeFilter: \['data-theme', 'data-theme-transition'\]/])assert.match(source,requirement)
 assert.doesNotMatch(source,/Math.random|getContext\(['"]webgl/)
})
