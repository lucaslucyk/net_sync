# Generated by Django 2.2.13 on 2020-08-31 14:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0011_auto_20200831_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='synchistory',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 8, 31, 11, 15, 17, 349628)),
        ),
    ]
