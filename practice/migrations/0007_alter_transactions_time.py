# Generated by Django 4.0.3 on 2022-04-03 04:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('practice', '0006_alter_transactions_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]