# Generated by Django 2.2.13 on 2020-08-28 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0006_synchistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credentialparameter',
            name='value',
            field=models.TextField(),
        ),
    ]
