# Generated by Django 2.2.3 on 2019-07-19 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0010_pagesection_graphs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagesection',
            name='graph',
        ),
    ]
