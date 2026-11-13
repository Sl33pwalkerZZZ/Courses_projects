import {spawn} from 'node:child_process';
import {readFileSync,writeFileSync,existsSync,openSync,closeSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
const mode=process.argv.includes('--preview')?'preview':process.argv.includes('--final')?'final':null;
if(!mode)throw Error('Specify --preview or --final');
const selected=process.argv.find(x=>x.startsWith('--video='))?.split('=')[1];
const videos=JSON.parse(readFileSync('content/quality-v2/series.json')).filter(v=>!selected||v.id===selected);
if(!videos.length)throw Error('Unknown video');
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const sourceHashes=()=>Object.fromEntries(['src/quality-v2/SeriesWorkspace.tsx','src/quality-v2/lesson113-series.tsx','content/quality-v2/series.json'].map(p=>[p,hash(p)]));
const inputs=sourceHashes();
if(mode==='final'){
 const r=JSON.parse(readFileSync('out/quality-v2/phase5h-frame-review.json'));
 if(!r.approved||r.scenes!==13||JSON.stringify(r.inputs)!==JSON.stringify(inputs))throw Error('Inspect all actual preview frames and freeze matching source before final export');
}
for(const v of videos){
 if(!['project-import','timeline-reopen'].includes(v.id))throw Error('Only new Videos2/3 allowed');
 const out=`out/quality-v2/${v.filename}-${mode==='preview'?'preview':'visual'}.mp4`;
 if(existsSync(out))throw Error('Refusing overwrite: '+out);
 const fd=openSync(`out/quality-v2/${v.id}-${mode}-render.log`,'w');
 const args=['render','src/quality-v2/lesson113-series.tsx',v.composition,out,'--codec=h264',`--crf=${mode==='preview'?21:18}`,'--concurrency=4',...(mode==='preview'?['--scale=0.5']:[])];
 console.log('Rendering',v.id,mode,v.seconds,'seconds');
 const result=await new Promise((ok,fail)=>{const p=spawn(resolve('node_modules/.bin/remotion'),args,{stdio:['ignore',fd,fd]});p.on('error',fail);p.on('exit',(code,signal)=>ok({code,signal}));});closeSync(fd);
 if(result.code!==0)throw Error(JSON.stringify({video:v.id,...result}));
 if(JSON.stringify(sourceHashes())!==JSON.stringify(inputs))throw Error('Source changed during render; do not approve this output');
 writeFileSync(`out/quality-v2/${v.id}-${mode}-render-inputs.json`,JSON.stringify(inputs,null,2)+'\n');
 console.log('Complete:',out);
}
