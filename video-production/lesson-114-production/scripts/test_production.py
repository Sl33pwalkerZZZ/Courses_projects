import unittest,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ProductionTests(unittest.TestCase):
 def test_structure_and_pacing(self):
  videos=json.loads((ROOT/'content/series.json').read_text());self.assertEqual(len(videos),3)
  for v in videos:
   self.assertEqual(sum(s['seconds'] for s in v['scenes']),v['seconds']);self.assertEqual(len(v['scenes']),7)
   self.assertLess(max(len((s['title']+' '+s['instruction']+' '+s['note']).split())/(s['seconds']-.22) for s in v['scenes']),3.8)
 def test_speech_provenance_and_real_caption_bounds(self):
  s=json.loads((ROOT/'content/speech.json').read_text());self.assertEqual(hashlib.sha256((ROOT/'public/f1-speech.wav').read_bytes()).hexdigest(),s['sha256']);self.assertEqual(s['seconds'],8.5625)
  end=0
  for c in s['captions']:self.assertGreaterEqual(c['startMs'],end);self.assertGreater(c['endMs'],c['startMs']);self.assertLessEqual(c['endMs'],s['seconds']*1000);end=c['endMs']
 def test_frozen_lesson_and_canonical_source(self):
  repo=ROOT.parents[1]
  snapshot_path=ROOT/'content/lesson114-readonly.json'
  snapshot=json.loads(snapshot_path.read_text())
  proposal=json.loads((ROOT/'content/lesson114-sync-proposal.json').read_text())
  plan=json.loads((repo/'courses/management/lesson114_quality_v2.json').read_text())
  source=json.loads((repo/'courses/management/media_module_5.json').read_text())['lessons'][1]
  change=plan['change']
  # Keep the historical pre-integration evidence frozen; never rewrite it to
  # match the eight subsequently approved paragraph edits.
  self.assertEqual(hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
                   'bc0fc4540761f9cda4b856f0f4baecf279e001fcf3a798085e8d20f029b062d5')
  self.assertEqual(plan['target'],proposal['target'])
  self.assertEqual((snapshot['id'],snapshot['module_id'],snapshot['order']),
                   (plan['target']['lesson_id'],plan['target']['module_id'],2))
  self.assertEqual(snapshot['title'],plan['expected']['title'])
  self.assertEqual(source['title'],snapshot['title'])
  self.assertEqual(snapshot['learning_content'],plan['expected']['learning_content'])
  self.assertEqual(snapshot['learning_content'],proposal['preserved_learning_content'])
  self.assertEqual(snapshot['text_content'],change['before'])
  for key in ('before','after','before_sha256','edits'):
   self.assertEqual(change[key],proposal[key],key)
  for key in ('before','after'):
   self.assertEqual(hashlib.sha256(change[key].encode()).hexdigest(),change[key+'_sha256'])
  text=snapshot['text_content']
  self.assertEqual(len(change['edits']),8)
  for edit in change['edits']:
   self.assertEqual(text.count(edit['before']),1)
   text=text.replace(edit['before'],edit['after'],1)
  # Exact whole-text equality rejects any unrelated additions, deletions or
  # substitutions, rather than merely checking that approved phrases exist.
  self.assertEqual(text,change['after'])
  self.assertEqual(source['text_content'],text)
  for key,count in (('objectives',3),('source_sections',9)):
   self.assertEqual(source[key],snapshot['learning_content'][key])
   self.assertEqual(len(source[key]),count)
  paragraphs=text.split('\n\n')
  positions=[]
  for number,heading in enumerate(source['source_sections'],1):
   self.assertTrue(heading.startswith(f'{number}. '))
   self.assertEqual(paragraphs.count(heading),1)
   positions.append(paragraphs.index(heading))
  self.assertEqual(positions,sorted(positions))
  anchors=[source['source_sections'][i] for i in (2,4,6)]
  videos=[a for a in plan['assets'] if a['kind']=='video']
  self.assertEqual(len(videos),3)
  self.assertEqual([a['metadata']['after_section'] for a in videos],anchors)
  self.assertEqual([a['after_section'] for a in proposal['placements']],anchors)
  self.assertEqual([Path(a['path']).name for a in videos],
                   [a['video'] for a in proposal['placements']])
  final=json.loads((ROOT/'content/final-assets.json').read_text())
  self.assertEqual((final['course_id'],final['module_id'],final['lesson_id']),
                   tuple(plan['target'][k] for k in ('course_id','module_id','lesson_id')))
  manifest=json.loads((repo/'docs/courses/media-module-5-assets.json').read_text())
  entries=[a for a in manifest['assets'] if a['course_lesson']==14 and a.get('filename')]
  self.assertEqual(len(entries),len(plan['assets']))
  for asset in plan['assets']:
   name=Path(asset['path']).name
   matches=[a for a in entries if a['filename']==name]
   self.assertEqual(len(matches),1)
   self.assertEqual(matches[0]['kind'],asset['kind'])
   self.assertEqual(matches[0]['sha256'],asset['sha256'])
   self.assertEqual(matches[0]['after_section'],asset['metadata']['after_section'])
   if asset['kind']=='video':
    recorded=[a for a in final['assets'] if Path(a['file']).name==name]
    self.assertEqual(len(recorded),1)
    self.assertEqual(recorded[0]['sha256'],asset['sha256'])
    self.assertEqual(recorded[0]['metadata']['after_section'],asset['metadata']['after_section'])
 def test_proposed_edits_preserve_anchors(self):
  p=json.loads((ROOT/'content/lesson114-sync-proposal.json').read_text());text=p['before'];self.assertEqual(len(p['edits']),8)
  for e in p['edits']:self.assertEqual(text.count(e['before']),1);text=text.replace(e['before'],e['after'],1)
  self.assertEqual(text,p['after'])
  for heading in p['preserved_learning_content']['source_sections']:self.assertEqual(text.split('\n\n').count(heading),1)
  self.assertEqual(len(p['preserved_learning_content']['objectives']),3)
 def test_spoken_vtt_is_real_bounded_sample_text(self):
  import re
  source=json.loads((ROOT/'content/speech.json').read_text())
  files=list((ROOT/'content').glob('*.vtt'));self.assertEqual(len(files),2)
  for file in files:
   blocks=file.read_text().strip().split('\n\n');self.assertEqual(blocks[0],'WEBVTT');last=-1
   for i,block in enumerate(blocks[1:]):
    times,text=block.split('\n',1);self.assertEqual(text,source['captions'][i%3]['text'])
    m=re.fullmatch(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})',times);self.assertIsNotNone(m)
    a=list(map(int,m.groups()));start=((a[0]*60+a[1])*60+a[2])*1000+a[3];end=((a[4]*60+a[5])*60+a[6])*1000+a[7]
    self.assertGreaterEqual(start,last);self.assertGreater(end,start);self.assertLessEqual(end,60000);last=end
 def test_caption_feedback_matches_visible_edits(self):
  import audio
  v=next(v for v in audio.DATA if v['id']=='caption-review');start=sum(s['seconds'] for s in v['scenes'][:3])
  self.assertIn((start+2,'place'),audio.EVENTS[v['id']])
  self.assertIn((start+4.5,'place'),audio.EVENTS[v['id']])
if __name__=='__main__':unittest.main(verbosity=2)
