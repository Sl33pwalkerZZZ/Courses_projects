"""Source-section creation uses existing lesson PATCH on disposable fixtures."""
from django.test import TestCase
from courses.models import Lesson, LessonAttachment
from . import test_section_renames as fixtures


class SectionCreationTests(TestCase):
    setUp = fixtures.SectionRenameTests.setUp

    def addition_payload(self, title='Third', body='New text'):
        return {'text_content': self.lesson.text_content+'\n\n'+title+'\n\n'+body,
                'learning_content': {'content_language':'ru','source_sections':['First','Second',title], 'objectives':['Goal'],'interactions':[]}}

    def test_plain_text_first_two_sections_round_trip_preview(self):
        lesson=Lesson.objects.create(module=self.lesson.module,title='New lesson',order=2,text_content='Original text.')
        url=f'/api/studio/lessons/{lesson.pk}/'
        body='Preparation\n\nOriginal text.\n\nFirst explanation\n\nCheck\n\nSecond explanation'
        payload={'text_content':body,'learning_content':{'content_language':'ru','source_sections':['Preparation','Check'],'objectives':[],'interactions':[]}}
        saved=self.client.patch(url,payload,format='json')
        self.assertEqual(saved.status_code,200,saved.data)
        read=self.client.get(f'/api/lessons/{lesson.pk}/').data
        self.assertEqual(read['text_content'],body)
        self.assertEqual(read['learning_content']['source_sections'],['Preparation','Check'])
        self.assertFalse(self.course.is_published)

    def test_append_and_rename_preserve_existing_anchors(self):
        payload=self.addition_payload()
        payload['text_content']=payload['text_content'].replace('First','Renamed')
        payload['learning_content']['source_sections'][0]='Renamed'
        payload['section_renames']=[{'from_title':'First','to_title':'Renamed'}]
        before=list(self.lesson.attachments.values())
        result=self.client.patch(self.url,payload,format='json')
        self.assertEqual(result.status_code,200,result.data)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.learning_content.source_sections,['Renamed','Second','Third'])
        for original,after in zip(before,self.lesson.attachments.values()):
            self.assertEqual(after,{**original,'after_section':'Renamed'})

    def test_invalid_additions_rejected_atomically(self):
        invalid=[]
        for heading in ['', 'First','Explanation','Line\nbreak']:
            invalid.append(self.addition_payload(heading))
        invalid.append(self.addition_payload('Third','Third'))
        invalid.append(self.addition_payload('Third',''))
        wrong_order=self.addition_payload();wrong_order['learning_content']['source_sections']=['First','Third','Second'];invalid.append(wrong_order)
        for payload in invalid:
            result=self.client.patch(self.url,payload,format='json')
            self.assertEqual(result.status_code,400,result.data)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.text_content,'First\n\nExplanation\n\nSecond\n\nEnd')
        self.assertEqual(self.lesson.learning_content.source_sections,['First','Second'])
        self.assertEqual(list(self.lesson.attachments.values_list('after_section',flat=True)),['First','First'])

    def test_unresolved_media_cannot_be_silently_adopted(self):
        LessonAttachment.objects.create(lesson=self.lesson,kind='srt',file='private/fake.srt',filename='fake.srt',after_section='Third',sha256='a'*64,order=4)
        result=self.client.patch(self.url,self.addition_payload(),format='json')
        self.assertEqual(result.status_code,400)
        self.assertIn('section_additions',result.data)

    def test_plain_update_and_authority_unchanged(self):
        self.assertEqual(self.client.patch(self.url,{'text_content':self.lesson.text_content+' extra'},format='json').status_code,200)
        self.course.is_published=True;self.course.save()
        self.assertEqual(self.client.patch(self.url,self.addition_payload(),format='json').status_code,400)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.patch(self.url,self.addition_payload(),format='json').status_code,401)
