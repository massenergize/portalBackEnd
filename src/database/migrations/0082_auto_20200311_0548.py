# Generated by Django 2.2.9 on 2020-03-11 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0081_auto_20200311_0524'),
    ]

    operations = [
        migrations.AddField(
            model_name='testimonial',
            name='anonymous',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='preferred_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]