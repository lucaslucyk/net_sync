# Generated by Django 2.2 on 2020-08-26 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_auto_20200826_1656'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sync',
            old_name='synchronyze',
            new_name='synchronize',
        ),
    ]
