# Generated by Django 3.0.14 on 2021-07-07 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0091_auto_20210702_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_recurring',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]