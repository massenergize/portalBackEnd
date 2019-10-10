# Generated by Django 2.2.5 on 2019-10-10 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carbon_calculator', '0010_auto_20191010_1341'),
        ('database', '0037_auto_20191010_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='calculator_action',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='carbon_calculator.Action'),
        ),
    ]
