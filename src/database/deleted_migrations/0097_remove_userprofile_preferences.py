# Generated by Django 3.0.14 on 2021-07-01 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0096_auto_20210621_1537'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='preferences',
        ),
    ]