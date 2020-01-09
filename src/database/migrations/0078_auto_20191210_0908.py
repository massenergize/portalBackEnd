# Generated by Django 2.2.8 on 2019-12-10 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0077_auto_20191210_0756'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='is_read',
            new_name='have_forwarded',
        ),
        migrations.AddField(
            model_name='message',
            name='have_replied',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]