# Generated by Django 2.2.13 on 2020-09-29 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0028_auto_20200928_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='syncprocess',
            name='expression',
            field=models.TextField(blank=True, help_text='Procedure that can process the origin response "origin_response".', null=True),
        ),
    ]
