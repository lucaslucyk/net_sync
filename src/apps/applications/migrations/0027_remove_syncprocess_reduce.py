# Generated by Django 2.2.13 on 2020-09-28 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0026_auto_20200928_1436'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='syncprocess',
            name='reduce',
        ),
    ]
