# Generated by Django 4.2.3 on 2023-07-13 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_watchlist_comment_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='end_time',
        ),
    ]