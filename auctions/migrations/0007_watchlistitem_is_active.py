# Generated by Django 4.2.3 on 2023-07-13 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_remove_watchlistitem_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlistitem',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
