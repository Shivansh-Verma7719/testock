# Generated by Django 4.0.2 on 2022-04-24 16:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('practice', '0006_alter_transactions_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 24, 16, 39, 17, 154750, tzinfo=utc)),
        ),
    ]
