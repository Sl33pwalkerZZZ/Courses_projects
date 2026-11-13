import {spawn} from 'node:child_process';
import {readFileSync,writeFileSync,existsSync,openSync,closeSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
const mode=process.argv.includes('--preview')?'previews':process.argv.includes('--final')?'final':null;
if(!mode)throw Error('Specify --preview or --final');
const data=JSON.parse(readFileSync('content/series.json'));
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const paths=['src/index.tsx','src/Workspace.tsx','content/series.json','content/speech.json'];
const hashes=()=>Object.fromEntries(paths.map(p=>[p,hash(p)]));const frozen=hashes();
if(mode==='final'){
 const review=JSON.parse(readFileSync('out/qa/frame-review.json'));
 if(!review.approved||review.scenes!==21||JSON.stringify(review.inputs)!==JSON.stringify(frozen))throw Error('Inspect21 actual preview frames and freeze source first');
}
async function run(cmd,args,log){const fd=openSync(log,'w');try{await new Promise((ok,fail)=>{const p=spawn(cmd,args,{stdio:['ignore',fd,fd]});p.on('error',fail);p.on('exit',code=>code===0?ok():fail(Error(cmd+' exit '+code)));});}finally{closeSync(fd);}}
for(const v of data){
 const visual=`out/${mode}/${v.filename}-visual.mp4`,target=`out/${mode}/${v.filename}.mp4`;
 if(existsSync(visual)||existsSync(target))throw Error('Refusing overwrite');
 console.log('Rendering',mode,v.id,v.seconds,flush());
 await run(resolve('node_modules/.bin/remotion'),['render','src/index.tsx',v.composition,visual,'--codec=h264',`--crf=${mode==='previews'?21:18}`,'--concurrency=4',...(mode==='previews'?['--scale=0.5']:[])],`out/qa/${mode}-${v.id}-render.log`);
 if(JSON.stringify(hashes())!==JSON.stringify(frozen))throw Error('Source changed during render; review output before use');
 const mix=`out/${v.filename}-mix.wav`;if(!existsSync(mix))throw Error('Prepare approved audio first');
 await run('ffmpeg',['-v','error','-n','-i',visual,'-i',mix,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-movflags','+faststart',target],`out/qa/${mode}-${v.id}-mux.log`);
 writeFileSync(`out/qa/${mode}-${v.id}-inputs.json`,JSON.stringify(frozen,null,2)+'\n');console.log('Complete',target);
}
function flush(){return '';}
