# Generated by Django 4.0.5 on 2022-06-11 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clicoh', '0005_alter_orderdetail_order_alter_orderdetail_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(),
        ),
    ]