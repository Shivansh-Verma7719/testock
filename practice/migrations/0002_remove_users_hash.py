# Generated by Django 4.0.2 on 2022-03-19 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('practice', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='hash',
        ),
    ]
