# Generated by Django 4.2.18 on 2025-01-15 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
