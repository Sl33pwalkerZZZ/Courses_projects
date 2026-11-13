"""Extract actual rendered scene and cut frames, no fabricated fixtures."""
from pathlib import Path
import json,subprocess,sys
from prepare_music_preview import ROOT
out=ROOT/'out/quality-v2';mode='final' if '--final' in sys.argv else 'preview'
indexes=[]
for v in json.loads((ROOT/'content/quality-v2/series.json').read_text()):
    video=out/(v['filename']+('' if mode=='final' else '-preview')+'.mp4')
    if not video.exists():raise SystemExit('Missing video: '+str(video))
    folder=out/('phase5h-frames-'+mode)/v['id'];folder.mkdir(parents=True,exist_ok=True)
    start=0;frames=[];cuts=[]
    for s in v['scenes']:
        frames.append(round((start+s['seconds']*.65)*30))
        if start:cuts.extend([start*30-1,start*30])
        start+=s['seconds']
    select='+'.join(f'eq(n,{frame})' for frame in frames)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{select}'",'-fps_mode','vfr',str(folder/'scene-%02d.png')],check=True)
    select='+'.join(f'eq(n,{frame})' for frame in cuts)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{select}',scale=480:270,tile=2x{len(cuts)//2}",'-frames:v','1',str(folder/'transitions.png')],check=True)
    indexes.extend({'video':v['id'],'scene':s['id'],'frame':f,'image':str((folder/f'scene-{i:02d}.png').relative_to(ROOT))} for i,(s,f) in enumerate(zip(v['scenes'],frames),1))
(out/('phase5h-frames-'+mode+'.json')).write_text(json.dumps(indexes,indent=2)+'\n')
print('Extracted',len(indexes),'actual scene frames plus all transition pairs')
