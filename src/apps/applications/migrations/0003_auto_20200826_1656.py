# Generated by Django 2.2 on 2020-08-26 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_auto_20200826_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='credential',
            name='comment',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='sync',
            name='synchronyze',
            field=models.CharField(choices=[('employees', 'Employees')], default=('employees', 'Employees'), max_length=20),
        ),
    ]