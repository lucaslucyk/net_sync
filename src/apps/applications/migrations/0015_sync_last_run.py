# Generated by Django 2.2.13 on 2020-09-01 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0014_auto_20200831_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='sync',
            name='last_run',
            field=models.DateTimeField(auto_now=True),
        ),
    ]