"""Isolated source/proposal regression checks; no Django setup or database writes."""
import hashlib,json,unittest
from pathlib import Path
from prepare_music_preview import ROOT
from phase5h_audio import events_for

class Phase5HTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'content/quality-v2/series.json').read_text())
        self.proposal=json.loads((ROOT/'content/quality-v2/lesson-113-sync-proposal.json').read_text())
    def test_only_new_videos_with_consistent_scene_lengths(self):
        self.assertEqual([(v['id'],v['seconds']) for v in self.data],[('project-import',47),('timeline-reopen',54)])
        self.assertEqual(sum(len(v['scenes']) for v in self.data),13)
        for v in self.data:
            self.assertEqual(sum(s['seconds'] for s in v['scenes']),v['seconds'])
            for e in events_for(v):
                self.assertIn(e['sound'],('select','place','finish'))
                self.assertLess(e['frame'],v['seconds']*30)
    def test_proposal_is_exact_narrow_and_reversible(self):
        p=self.proposal
        self.assertEqual(p['target']['lesson_id'],113)
        self.assertEqual(p['target']['course_id'],10)
        self.assertEqual(len(p['changes']),1)
        c=p['changes'][0];self.assertEqual(c['field'],'Lesson.text_content')
        self.assertEqual(hashlib.sha256(c['before'].encode()).hexdigest(),p['expected_before']['text_sha256'])
        value=c['before']
        for e in c['edits']:
            self.assertEqual(value.count(e['before']),1)
            value=value.replace(e['before'],e['after'],1)
        self.assertEqual(value,c['after'])
        self.assertEqual(hashlib.sha256(value.encode()).hexdigest(),c['after_sha256'])
        for e in reversed(c['edits']):
            self.assertEqual(value.count(e['after']),1)
            value=value.replace(e['after'],e['before'],1)
        self.assertEqual(value,c['before'])
    def test_all_nine_anchors_and_three_objectives_preserved(self):
        p=self.proposal;self.assertEqual(len(p['expected_before']['objectives']),3)
        headings=p['expected_before']['source_sections'];self.assertEqual(len(headings),9)
        c=p['changes'][0]
        for text in [c['before'],c['after']]:
            blocks=text.split('\n\n')
            self.assertEqual([b for b in blocks if b in headings],headings)
    def test_accessible_equivalents_complete_and_within_upload_limit(self):
        for n,stem in enumerate(['m5-l13-v1-source-organization-quality-v2']+[v['filename'] for v in self.data],1):
            equivalent=(ROOT/'content/quality-v2'/f'{stem}.equivalent.ru.txt').read_text()
            self.assertTrue(100<len(equivalent)<20000)
            self.assertIn('схем',equivalent.casefold())
            self.assertTrue((ROOT/'content/quality-v2'/f'{stem}.transcript.ru.md').is_file())
    def test_original_composition_not_registered_for_new_render(self):
        entry=(ROOT/'src/quality-v2/lesson113-series.tsx').read_text()
        self.assertNotIn('SourceOrganizationQualityV2',entry)
        self.assertNotIn('QualityVideo',entry)

if __name__=='__main__':unittest.main(verbosity=2)
