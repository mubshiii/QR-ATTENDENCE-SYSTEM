# Generated by Django 5.0.4 on 2024-06-11 10:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_branch_year_course_branch_student_branch_course_year_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RollNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='roll_no',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='attendance.rollnumber'),
        ),
    ]