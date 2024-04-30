# Generated by Django 4.2.9 on 2024-02-16 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('userid', models.CharField(max_length=33, unique=True)),
                ('display_name', models.CharField(max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]