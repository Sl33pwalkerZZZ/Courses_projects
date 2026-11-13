"""Extract a representative rendered frame from every scene, with exact indices."""
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[1]
mode='final' if '--final' in sys.argv else 'previews'
indexes=[]
for v in json.loads((root/'content/videos.json').read_text()):
 video=root/'out'/mode/(v['filename']+('' if mode=='final' else '-preview')+'.mp4')
 if not video.exists():continue
 frames=[];start=0
 for scene in v['scenes']:
  frames.append((round((start+max(scene['actionAt']+.8,scene['seconds']*.55))*30),scene));start+=scene['seconds']
 folder=root/'out/qa'/mode/v['id'];folder.mkdir(parents=True,exist_ok=True)
 select='+'.join(f'eq(n,{f})' for f,_ in frames)
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf',f"select='{select}'",'-fps_mode','vfr',str(folder/'scene-%02d.png')],check=True)
 for i,(frame,s) in enumerate(frames,1):indexes.append(dict(video=v['id'],scene=s['id'],title=s['title'],frame=frame,image=str((folder/f'scene-{i:02d}.png').relative_to(root))))
(root/f'out/qa/{mode}-frames.json').write_text(json.dumps(indexes,ensure_ascii=False,indent=2)+'\n')
print('Extracted',len(indexes),'actual rendered scene frames.')
