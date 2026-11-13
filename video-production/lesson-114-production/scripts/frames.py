"""Actual rendered frame samples and adjacent scene-cut contact sheets."""
from pathlib import Path
import subprocess,json,sys
ROOT=Path(__file__).resolve().parents[1];mode='final' if '--final' in sys.argv else 'previews';index=[]
selected=next((x.split('=',1)[1] for x in sys.argv if x.startswith('--video=')),None)
for v in json.loads((ROOT/'content/series.json').read_text()):
 if selected and v['id']!=selected:continue
 video=ROOT/'out'/mode/(v['filename']+'.mp4')
 if not video.exists():raise SystemExit('Missing '+str(video))
 folder=ROOT/'out/qa'/('frames-'+mode)/v['id'];folder.mkdir(parents=True,exist_ok=True)
 offset=0;frames=[];cuts=[]
 for s in v['scenes']:
  frames.append(round((offset+s['seconds']*.65)*30))
  if offset:cuts.extend([offset*30-1,offset*30])
  offset+=s['seconds']
 select='+'.join(f'eq(n,{x})' for x in frames)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{select}'",'-fps_mode','vfr',str(folder/'scene-%02d.png')],check=True)
 select='+'.join(f'eq(n,{x})' for x in cuts)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{select}',scale=480:270,tile=2x6",'-frames:v','1',str(folder/'transitions.png')],check=True)
 index.extend({'video':v['id'],'scene':s['id'],'frame':f,'path':str((folder/f'scene-{i:02d}.png').relative_to(ROOT))} for i,(s,f) in enumerate(zip(v['scenes'],frames),1))
(ROOT/'out/qa'/('frames-'+mode+('-'+selected if selected else '')+'.json')).write_text(json.dumps(index,indent=2)+'\n');print('Extracted',len(index),'actual scene frames with before/after transition pairs')
