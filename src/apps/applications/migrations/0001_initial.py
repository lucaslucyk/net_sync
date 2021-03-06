# Generated by Django 2.2 on 2020-08-26 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application', models.CharField(choices=[('nettime6', 'NetTime 6'), ('manager', 'SPEC Manager'), ('visma', 'Visma RH')], default=('nettime6', 'NetTime 6'), max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Sync',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('synchronyze', models.CharField(choices=[('nettime6', 'NetTime 6'), ('manager', 'SPEC Manager'), ('visma', 'Visma RH')], default=('nettime6', 'NetTime 6'), max_length=20)),
                ('destiny', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destiny', to='applications.Credential')),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin', to='applications.Credential')),
            ],
        ),
        migrations.CreateModel(
            name='SyncParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('use_in', models.CharField(choices=[('origin', 'Origin'), ('destiny', 'Destiny')], default='origin', max_length=20)),
                ('sync', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.Sync')),
            ],
        ),
        migrations.CreateModel(
            name='CredentialParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('host', 'Host'), ('server', 'Server'), ('instance', 'Instance'), ('user', 'User'), ('password', 'Password')], default=('host', 'Host'), max_length=20)),
                ('value', models.CharField(max_length=200)),
                ('credential', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.Credential')),
            ],
        ),
    ]
