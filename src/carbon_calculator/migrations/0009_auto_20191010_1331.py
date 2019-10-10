# Generated by Django 2.2.5 on 2019-10-10 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carbon_calculator', '0008_auto_20190930_1936'),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='cc_media/')),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'cc_media',
            },
        ),
        migrations.RemoveField(
            model_name='action',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='event',
            name='host_logo',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sponsor_logo',
        ),
    ]