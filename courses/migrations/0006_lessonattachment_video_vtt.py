from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('courses', '0005_lessonattachment')]
    operations = [migrations.AlterField(model_name='lessonattachment', name='kind', field=models.CharField(max_length=10, choices=[('audio', 'Audio'), ('srt', 'Subtitles'), ('video', 'Video'), ('vtt', 'WebVTT')]))]
