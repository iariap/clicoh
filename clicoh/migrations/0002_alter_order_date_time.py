# Generated by Django 4.0.5 on 2022-06-09 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clicoh', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
