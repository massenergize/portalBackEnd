# Generated by Django 2.2.5 on 2019-09-30 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carbon_calculator', '0007_auto_20190930_1150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='shortname',
        ),
        migrations.AddField(
            model_name='event',
            name='displayname',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='station',
            name='displayname',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='event',
            name='datetime',
            field=models.DateTimeField(blank=True),
        ),
    ]