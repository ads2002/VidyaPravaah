# Generated by Django 4.2.5 on 2023-09-22 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elearn', '0023_remove_learnerparentconnection_student_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parent',
            name='learner_linked',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='elearn.learner'),
        ),
    ]
