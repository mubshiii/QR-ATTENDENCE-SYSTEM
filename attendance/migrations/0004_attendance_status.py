# Generated by Django 5.0.4 on 2024-06-11 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_rollnumber_student_roll_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='status',
            field=models.CharField(default=True, max_length=10),
        ),
    ]