# Generated by Django 2.2.13 on 2021-01-26 23:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0032_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='credential',
            name='company',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='applications.Company'),
        ),
    ]
