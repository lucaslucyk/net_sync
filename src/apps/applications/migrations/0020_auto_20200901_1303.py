# Generated by Django 2.2.13 on 2020-09-01 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0019_sync_cron_expression'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sync',
            name='cron_expression',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]