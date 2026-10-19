from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("progress", "0003_enrollmentrequest"),
        ("courses", "0004_assignment_learning_activity_courseimport_and_more"),
    ]
    operations = [
        migrations.AddField(model_name="assignmentsubmission", name="is_structured", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="assignmentsubmission", name="payload", field=models.JSONField(blank=True, default=dict)),
        migrations.AddField(model_name="assignmentsubmission", name="revision", field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name="assignmentsubmission", name="review_history", field=models.JSONField(blank=True, default=list)),
        migrations.AlterField(model_name="assignmentsubmission", name="status", field=models.CharField(
            choices=[("draft", "Черновик"), ("pending", "На проверке"), ("approved", "Принято"), ("rejected", "Отклонено")],
            default="pending", max_length=20,
        )),
        migrations.AddConstraint(model_name="assignmentsubmission", constraint=models.UniqueConstraint(
            fields=("student", "assignment"), condition=models.Q(is_structured=True), name="one_structured_assignment_per_student",
        )),
    ]
